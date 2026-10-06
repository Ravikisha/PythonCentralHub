/**
 * Firestore side of progress tracking.
 *
 * Loaded only through a dynamic `import()` from local.ts, so the Firestore SDK
 * reaches the browser when a reader first marks something -- not on page load,
 * and never at all for someone who only reads.
 *
 * Shape under `users/{uid}`:
 *
 *   progress/{moduleSlug}   { completed: string[], updatedAt }
 *   stats/summary           { streak, longest, lastActive, totalCompleted }
 *   stats/bookmarks         { pages: string[] }
 *   stats/quizzes           { [encodedKey]: { correct, total, at } }
 *   stats/notes             { [encodedPageId]: string }
 *   stats/exercises         { [encodedKey]: epoch millis of first pass }
 *
 * One document per module rather than one per page: a reader can finish
 * hundreds of pages, and a document each would turn the dashboard into
 * hundreds of reads. Twelve module documents cover the whole curriculum.
 */
import { getDb } from "../firebase/client";
import { signedInAccount } from "../firebase/auth";
import { encodeId, decodeId, moduleOf } from "./ids";
import type { PendingOp, ProgressState, QuizResult } from "./local";
import { read, replace } from "./local";

/**
 * Raised when a sync is attempted without a signed-in account.
 *
 * Not an error condition: a guest's progress is supposed to stay in
 * localStorage. Callers catch this and carry on quietly.
 */
export class NotSignedIn extends Error {
  constructor() {
    super("progress sync skipped: no signed-in account");
    this.name = "NotSignedIn";
  }
}

/**
 * uid to write under.
 *
 * Nothing here ever creates an account. Guests -- including anyone still
 * holding an anonymous session from an earlier build -- are refused, so the
 * database only ever holds progress belonging to a real, recoverable login.
 */
async function uid(): Promise<string> {
  const user = await signedInAccount();
  if (!user) throw new NotSignedIn();
  return user.uid;
}

/* -------------------------------------------------------------------------- */
/* Push                                                                        */
/* -------------------------------------------------------------------------- */

/**
 * Apply a batch of buffered changes.
 *
 * Completions use arrayUnion/arrayRemove rather than writing the whole array,
 * so two devices editing different pages of the same module merge instead of
 * overwriting each other.
 */
export async function pushOps(ops: PendingOp[], state: ProgressState): Promise<void> {
  if (!ops.length) return;

  const fs = await import("firebase/firestore");
  const db = await getDb();
  const id = await uid();

  const batch = fs.writeBatch(db);
  const userDoc = (...path: string[]) => fs.doc(db, "users", id, ...path);

  /* completions, grouped so one module is one document write */
  const added = new Map<string, string[]>();
  const removed = new Map<string, string[]>();
  const push = (map: Map<string, string[]>, mod: string, pageId: string) => {
    const list = map.get(mod) ?? [];
    list.push(pageId);
    map.set(mod, list);
  };

  const bookmarksAdded: string[] = [];
  const bookmarksRemoved: string[] = [];
  const quizzes: Record<string, QuizResult> = {};
  const notes: Record<string, unknown> = {};
  const exercises: Record<string, number> = {};

  for (const op of ops) {
    switch (op.kind) {
      case "complete":
        push(added, op.module, op.pageId);
        break;
      case "uncomplete":
        push(removed, op.module, op.pageId);
        break;
      case "bookmark":
        bookmarksAdded.push(op.pageId);
        break;
      case "unbookmark":
        bookmarksRemoved.push(op.pageId);
        break;
      case "quiz":
        quizzes[encodeId(op.key)] = { correct: op.correct, total: op.total, at: Date.now() };
        break;
      case "exercise":
        exercises[encodeId(op.key)] = op.at;
        break;
      case "enrol":
        // Carried by the summary document written below on every flush.
        break;
      case "note":
        // An emptied note is deleted rather than stored blank, so the cloud
        // copy matches what the local store just did.
        notes[encodeId(op.pageId)] = op.text ? op.text : fs.deleteField();
        break;
    }
  }

  for (const [mod, pages] of added) {
    batch.set(
      userDoc("progress", mod),
      { completed: fs.arrayUnion(...pages), updatedAt: fs.serverTimestamp() },
      { merge: true }
    );
  }
  for (const [mod, pages] of removed) {
    batch.set(
      userDoc("progress", mod),
      { completed: fs.arrayRemove(...pages), updatedAt: fs.serverTimestamp() },
      { merge: true }
    );
  }

  if (bookmarksAdded.length || bookmarksRemoved.length) {
    const changes: Record<string, unknown> = { updatedAt: fs.serverTimestamp() };
    if (bookmarksAdded.length) changes.pages = fs.arrayUnion(...bookmarksAdded);
    // A single write cannot both union and remove on one field, so a batch
    // that does both keeps the removals for a second set() below.
    batch.set(userDoc("stats", "bookmarks"), changes, { merge: true });
    if (bookmarksRemoved.length) {
      batch.set(
        userDoc("stats", "bookmarks"),
        { pages: fs.arrayRemove(...bookmarksRemoved) },
        { merge: true }
      );
    }
  }

  if (Object.keys(quizzes).length) {
    batch.set(userDoc("stats", "quizzes"), quizzes, { merge: true });
  }

  if (Object.keys(notes).length) {
    batch.set(userDoc("stats", "notes"), notes, { merge: true });
  }

  batch.set(
    userDoc("stats", "summary"),
    {
      streak: state.streak.count,
      longest: state.streak.longest,
      lastActive: state.streak.last,
      totalCompleted: Object.values(state.modules).reduce((n, l) => n + l.length, 0),
      enrolled: state.enrolled ?? [],
      updatedAt: fs.serverTimestamp(),
    },
    { merge: true }
  );

  await batch.commit();
  if (Object.keys(exercises).length) await pushExercises(id, exercises);
}

/**
 * Exercise passes, written on their own after the main batch.
 *
 * stats/exercises is newer than the rest. Until the Firestore rules that allow
 * it are deployed the write is refused, and inside the main batch that refusal
 * would take every other progress write down with it.
 */
async function pushExercises(id: string, exercises: Record<string, number>): Promise<void> {
  try {
    const fs = await import("firebase/firestore");
    const db = await getDb();
    await fs.setDoc(fs.doc(db, "users", id, "stats", "exercises"), exercises, { merge: true });
  } catch (err) {
    console.warn("[progress] exercise passes not synced:", err);
  }
}

/* -------------------------------------------------------------------------- */
/* Pull                                                                        */
/* -------------------------------------------------------------------------- */

/** Everything stored for the current user, as a local-shaped state object. */
async function fetchCloud(id: string): Promise<Partial<ProgressState>> {
  const fs = await import("firebase/firestore");
  const db = await getDb();

  const [progressSnap, bookmarksSnap, quizSnap, summarySnap, notesSnap, exerciseData] =
    await Promise.all([
      fs.getDocs(fs.collection(db, "users", id, "progress")),
      fs.getDoc(fs.doc(db, "users", id, "stats", "bookmarks")),
      fs.getDoc(fs.doc(db, "users", id, "stats", "quizzes")),
      fs.getDoc(fs.doc(db, "users", id, "stats", "summary")),
      fs.getDoc(fs.doc(db, "users", id, "stats", "notes")),
      // Refused until the rules allowing it are deployed; see pushExercises.
      fs
        .getDoc(fs.doc(db, "users", id, "stats", "exercises"))
        .then((d) => (d.data() ?? {}) as Record<string, number>)
        .catch(() => ({}) as Record<string, number>),
    ]);

  const modules: Record<string, string[]> = {};
  progressSnap.forEach((d) => {
    const completed = (d.data().completed ?? []) as string[];
    if (completed.length) modules[d.id] = completed;
  });

  const summary = summarySnap.data() ?? {};

  return {
    modules,
    bookmarks: (bookmarksSnap.data()?.pages ?? []) as string[],
    // Stored with "/" encoded (Firestore keys), used locally in the raw
    // "page/id#0" form recordQuiz() looks up. Decoded here, like notes.
    quizzes: Object.fromEntries(
      Object.entries((quizSnap.data() ?? {}) as Record<string, QuizResult>).map(
        ([k, v]) => [decodeId(k), v],
      ),
    ),
    exercises: Object.fromEntries(
      Object.entries(exerciseData).map(([k, v]) => [decodeId(k), v]),
    ),
    notes: Object.fromEntries(
      Object.entries((notesSnap.data() ?? {}) as Record<string, string>).map(([k, v]) => [
        decodeId(k),
        v,
      ])
    ),
    streak: {
      last: (summary.lastActive as string) ?? "",
      count: (summary.streak as number) ?? 0,
      longest: (summary.longest as number) ?? 0,
    },
    enrolled: Array.isArray(summary.enrolled) ? (summary.enrolled as string[]) : [],
  };
}

/** Union of two page-id lists, order-independent. */
function union(a: string[] = [], b: string[] = []): string[] {
  return [...new Set([...a, ...b])];
}

/**
 * Reconcile the cloud copy into local state.
 *
 * Always a union, never a replacement. A learner who marked pages on their
 * phone and others on their laptop should end up with both sets; picking a
 * winner by timestamp would silently throw one device's work away. Un-marking
 * a page is the one thing a union cannot express, so an un-mark only sticks
 * once it has been flushed (which the debounce makes near-immediate).
 */
export async function mergeWithCloud(): Promise<ProgressState> {
  const id = await uid();
  const cloud = await fetchCloud(id);
  const local = read();

  const modules: Record<string, string[]> = { ...local.modules };
  for (const [mod, pages] of Object.entries(cloud.modules ?? {})) {
    modules[mod] = union(modules[mod], pages);
  }

  // Raw keys throughout. The merge used to write encoded keys into local
  // storage, where recordQuiz() looks up raw ones: a retake then missed the
  // stored best, saved a duplicate, and the push overwrote the cloud best
  // with the lower score. decodeId() on local keys also heals stores that
  // already hold encoded duplicates (it leaves raw keys unchanged).
  const quizzes = { ...(cloud.quizzes ?? {}) };
  for (const [key, result] of Object.entries(local.quizzes)) {
    const raw = decodeId(key);
    const existing = quizzes[raw];
    if (!existing || existing.correct < result.correct) quizzes[raw] = result;
  }

  // Notes merge by recency of edit is not available (no per-note timestamp),
  // so the local copy wins for any page edited on this device and the cloud
  // fills in the rest. Losing a note would be worse than keeping a stale one.
  const notes = { ...(cloud.notes ?? {}), ...local.notes };

  // A union keyed by exercise, keeping the earlier pass.
  const exercises = { ...(cloud.exercises ?? {}) };
  for (const [key, at] of Object.entries(local.exercises ?? {})) {
    exercises[key] = Math.min(at, exercises[key] ?? at);
  }

  const merged: ProgressState = {
    v: 1,
    modules,
    bookmarks: union(local.bookmarks, cloud.bookmarks),
    enrolled: union(local.enrolled, cloud.enrolled),
    quizzes,
    exercises,
    notes,
    streak: {
      last: local.streak.last > (cloud.streak?.last ?? "") ? local.streak.last : cloud.streak!.last,
      count: Math.max(local.streak.count, cloud.streak?.count ?? 0),
      longest: Math.max(local.streak.longest, cloud.streak?.longest ?? 0),
    },
    hydrated: true,
  };

  replace(merged);
  await pushMerged(id, merged);
  return merged;
}

/** Write the reconciled state back so both sides agree. */
async function pushMerged(id: string, state: ProgressState): Promise<void> {
  const fs = await import("firebase/firestore");
  const db = await getDb();
  const batch = fs.writeBatch(db);

  for (const [mod, pages] of Object.entries(state.modules)) {
    batch.set(
      fs.doc(db, "users", id, "progress", mod),
      { completed: pages, updatedAt: fs.serverTimestamp() },
      { merge: true }
    );
  }
  batch.set(
    fs.doc(db, "users", id, "stats", "bookmarks"),
    { pages: state.bookmarks, updatedAt: fs.serverTimestamp() },
    { merge: true }
  );
  batch.set(
    fs.doc(db, "users", id, "stats", "quizzes"),
    Object.fromEntries(Object.entries(state.quizzes).map(([k, v]) => [encodeId(k), v])),
    { merge: true },
  );
  batch.set(
    fs.doc(db, "users", id, "stats", "notes"),
    Object.fromEntries(Object.entries(state.notes).map(([k, v]) => [encodeId(k), v])),
    { merge: true }
  );
  batch.set(
    fs.doc(db, "users", id, "stats", "summary"),
    {
      streak: state.streak.count,
      longest: state.streak.longest,
      lastActive: state.streak.last,
      totalCompleted: Object.values(state.modules).reduce((n, l) => n + l.length, 0),
      enrolled: state.enrolled ?? [],
      updatedAt: fs.serverTimestamp(),
    },
    { merge: true }
  );

  await batch.commit();
  await pushExercises(
    id,
    Object.fromEntries(Object.entries(state.exercises ?? {}).map(([k, v]) => [encodeId(k), v])),
  );
}

/**
 * Pull the cloud copy once per device.
 *
 * Called from the dashboard and after sign-in, never from a content page: a
 * content page only needs the local copy, and hydrating from all of them
 * would put a read on every page view.
 */
export async function hydrateOnce(): Promise<ProgressState> {
  const local = read();
  if (local.hydrated) return local;
  return mergeWithCloud();
}

/** Force a re-pull, e.g. after signing in as a different account. */
export async function resync(): Promise<ProgressState> {
  return mergeWithCloud();
}

export { moduleOf };
