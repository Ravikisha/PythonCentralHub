"use client";

import { useEffect, useMemo, useState } from "react";
import type { User } from "firebase/auth";
import { BadgeCheck, Download, Mail, ShieldAlert } from "lucide-react";
import { SiGithub, SiGoogle } from "@icons-pack/react-simple-icons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { StatusLine, type Status } from "@/components/auth/StatusLine";
import { Avatar } from "@/components/auth/Avatar";
import { SessionLoading, SignedOutGate } from "@/components/auth/SignedOutGate";
import { useSession } from "@/components/auth/useSession";
import { errorMessage } from "@/components/auth/session";
import {
  read,
  subscribe,
  currentStreak,
  type ProgressState,
} from "@/src/lib/progress/local";
import { t } from "@/lib/strings";
import { SITE_NAME, SITE_SLUG } from "@/lib/site";

/**
 * /profile -- the learner's own record.
 *
 * Deliberately not a second dashboard. The dashboard answers "how far through
 * the course am I"; this page answers three questions it does not:
 *
 *   - Where does my reading actually go? (the split across courses)
 *   - How am I doing on the questions, not just the pages? (quiz accuracy)
 *   - What is this account, and what does it share? (providers, verification,
 *     the two opt-ins, the export, the delete)
 *
 * Everything on the left is read from the same local progress store the
 * sidebar and the dashboard use, so the three always agree without a fetch.
 */
const PROVIDER_LABELS: Record<string, string> = {
  "google.com": "Google",
  "github.com": "GitHub",
  password: "Email and password",
};

const PROVIDER_ICONS: Record<
  string,
  React.ComponentType<{ className?: string }>
> = {
  "google.com": SiGoogle,
  "github.com": SiGithub,
  password: Mail,
};

interface ManifestModule {
  slug: string;
  label: string;
  count: number;
}

type Prefs = Record<string, boolean>;

export function ProfilePanel() {
  const session = useSession();

  if (session.state === "loading") return <SessionLoading />;
  if (session.state === "signed-out") return <SignedOutGate next="/profile/" />;

  return <Account user={session.user} />;
}

function Account({ user }: { user: User }) {
  const [status, setStatus] = useState<Status | null>(null);

  return (
    <div className="prof">
      <Record user={user} />

      <div className="prof__controls">
        <Identity user={user} onStatus={setStatus} />
        <Preferences user={user} onStatus={setStatus} />
        <YourData onStatus={setStatus} />
        <StatusLine status={status} />
        <DangerZone onStatus={setStatus} />
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* The record                                                                  */
/* -------------------------------------------------------------------------- */

function Record({ user }: { user: User }) {
  const [state, setState] = useState<ProgressState | null>(null);
  const [modules, setModules] = useState<ManifestModule[]>([]);
  const [certificates, setCertificates] = useState<number | null>(null);

  useEffect(() => {
    setState(read());
    return subscribe(setState);
  }, []);

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      try {
        const res = await fetch("/progress-manifest.json");
        if (res.ok && !cancelled)
          setModules(((await res.json()).modules ?? []) as ManifestModule[]);
      } catch {
        /* the split just falls back to raw slugs */
      }

      try {
        const { doc, getDoc } = await import("firebase/firestore");
        const { getDb } = await import("@/src/lib/firebase/client");
        const snap = await getDoc(
          doc(await getDb(), "users", user.uid, "stats", "certificates"),
        );
        if (!cancelled)
          setCertificates(((snap.data()?.items ?? []) as unknown[]).length);
      } catch {
        if (!cancelled) setCertificates(0);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [user.uid]);

  const reading = useMemo(() => {
    if (!state) return null;

    // The manifest is fetched, so for the first frame -- and if it fails --
    // fall back to a readable form of the slug rather than "dsa with python".
    const label = (slug: string) =>
      modules.find((m) => m.slug === slug)?.label ??
      slug
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");

    const split = Object.entries(state.modules)
      .map(([slug, pages]) => ({
        slug,
        label: label(slug),
        pages: pages.length,
      }))
      .filter((row) => row.pages > 0)
      .sort((a, b) => b.pages - a.pages);

    const pages = split.reduce((n, row) => n + row.pages, 0);

    const attempts = Object.values(state.quizzes);
    const correct = attempts.reduce((n, q) => n + q.correct, 0);
    const asked = attempts.reduce((n, q) => n + q.total, 0);

    return {
      split,
      pages,
      quizzes: attempts.length,
      accuracy: asked ? Math.round((correct / asked) * 100) : null,
      correct,
      asked,
      notes: Object.keys(state.notes).length,
      bookmarks: state.bookmarks.length,
      streak: state.streak,
    };
  }, [state, modules]);

  const since = user.metadata.creationTime
    ? new Date(user.metadata.creationTime).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : null;

  if (!reading)
    return (
      <div className="prof__record app__loading">{t("pch.authLoading")}</div>
    );

  return (
    <section className="prof__record" aria-labelledby="prof-record">
      <h2 id="prof-record" className="prof__h2">
        Your reading
      </h2>

      {reading.pages === 0 ? (
        <p className="prof__empty">
          Nothing marked complete yet. Open a lesson in any course and press
          “Mark as complete” at the end of it. This is where it adds up.
        </p>
      ) : (
        <>
          {/* One bar, the whole of the reading, split by course. The largest
              course takes the cover gradient; the rest are hairline greys, so
              the shape of someone's attention reads at a glance. */}
          <div
            className="prof__bar"
            role="img"
            aria-label={reading.split
              .map((row) => `${row.label}: ${row.pages} lessons`)
              .join(", ")}
          >
            {reading.split.map((row, i) => (
              <span
                key={row.slug}
                className="prof__bar-seg"
                data-lead={i === 0 ? "true" : undefined}
                style={{ width: `${(row.pages / reading.pages) * 100}%` }}
              />
            ))}
          </div>

          <ul className="prof__legend">
            {reading.split.slice(0, 5).map((row, i) => (
              <li key={row.slug}>
                <span
                  className="prof__dot"
                  data-lead={i === 0 ? "true" : undefined}
                />
                <span className="prof__legend-name">{row.label}</span>
                <span className="prof__legend-n">{row.pages}</span>
              </li>
            ))}
            {reading.split.length > 5 ? (
              <li className="prof__legend-rest">
                and {reading.split.length - 5} more{" "}
                {reading.split.length - 5 === 1 ? "course" : "courses"}
              </li>
            ) : null}
          </ul>
        </>
      )}

      <dl className="prof__figures">
        <Figure value={reading.pages} label="lessons done" />
        <Figure
          value={reading.accuracy === null ? "—" : `${reading.accuracy}%`}
          label={
            reading.quizzes === 0
              ? "quiz accuracy"
              : `quiz accuracy, ${reading.correct} of ${reading.asked}`
          }
        />
        <Figure
          value={currentStreak(state!)}
          label="day streak"
          hint={`longest ${reading.streak.longest}`}
        />
        <Figure
          value={certificates === null ? "—" : certificates}
          label={certificates === 1 ? "certificate" : "certificates"}
        />
      </dl>

      <p className="prof__aside">
        {reading.bookmarks > 0 || reading.notes > 0 ? (
          <>
            You have {reading.bookmarks} saved{" "}
            {reading.bookmarks === 1 ? "page" : "pages"} and {reading.notes}{" "}
            private {reading.notes === 1 ? "note" : "notes"}. Notes stay on your
            account; nobody else can read them.
          </>
        ) : (
          <>
            Bookmark a page or leave yourself a note while reading — both show
            up here and on the dashboard.
          </>
        )}
      </p>

      {since ? (
        <p className="prof__since">Reading here since {since}.</p>
      ) : null}
    </section>
  );
}

function Figure({
  value,
  label,
  hint,
}: {
  value: string | number;
  label: string;
  hint?: string;
}) {
  return (
    <div className="prof__figure">
      <dt className="prof__figure-label">
        {label}
        {hint ? <span className="prof__figure-hint">{hint}</span> : null}
      </dt>
      <dd className="prof__figure-value">{value}</dd>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Identity                                                                    */
/* -------------------------------------------------------------------------- */

function Identity({
  user,
  onStatus,
}: {
  user: User;
  onStatus: (status: Status | null) => void;
}) {
  const [displayName, setDisplayName] = useState(user.displayName ?? "");
  const [busy, setBusy] = useState(false);
  const [sending, setSending] = useState(false);

  const dirty = displayName.trim() !== (user.displayName ?? "");

  // Where the picture comes from, for the line under it. Same resolution as
  // the header: the account's own photo first, then any linked provider's.
  const photoProvider =
    user.providerData.find((p) => p.photoURL && p.photoURL === user.photoURL) ??
    user.providerData.find((p) => p.photoURL);
  const photo = user.photoURL || photoProvider?.photoURL || "";
  const photoSource =
    PROVIDER_LABELS[photoProvider?.providerId ?? ""] ?? "your sign-in provider";
  const hasPassword = user.providerData.some(
    (p) => p.providerId === "password",
  );

  // Shown so a reader can spot a session they do not recognise -- the only
  // security signal this page can offer without a server.
  const lastSeen = user.metadata.lastSignInTime
    ? new Date(user.metadata.lastSignInTime).toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
      })
    : "—";

  async function save(event: React.FormEvent) {
    event.preventDefault();
    onStatus(null);
    setBusy(true);
    try {
      const { updateDisplayName } = await import("@/src/lib/firebase/auth");
      await updateDisplayName(displayName.trim());
      onStatus({ text: t("pch.authSaved"), tone: "success" });
    } catch (err) {
      onStatus({ text: await errorMessage(err), tone: "error" });
    } finally {
      setBusy(false);
    }
  }

  async function verify() {
    setSending(true);
    onStatus(null);
    try {
      const { sendVerification } = await import("@/src/lib/firebase/auth");
      await sendVerification();
      onStatus({ text: t("pch.authVerifySent"), tone: "success" });
    } catch (err) {
      onStatus({ text: await errorMessage(err), tone: "error" });
    } finally {
      setSending(false);
    }
  }

  async function resetPassword() {
    if (!user.email) return;
    setSending(true);
    onStatus(null);
    try {
      const { sendPasswordReset } = await import("@/src/lib/firebase/auth");
      await sendPasswordReset(user.email);
      onStatus({ text: t("pch.authResetSent"), tone: "success" });
    } catch (err) {
      onStatus({ text: await errorMessage(err), tone: "error" });
    } finally {
      setSending(false);
    }
  }

  return (
    <section className="prof__block" aria-labelledby="prof-identity">
      <h2 id="prof-identity" className="prof__h2">
        Your details
      </h2>

      <div className="prof__who">
        <Avatar photo={photo} seed={user.uid} size={64} />
        <div className="prof__who-lines">
          <span className="prof__who-name">
            {user.displayName || user.email || "Your account"}
          </span>
          <span className="prof__row-hint">
            {photo
              ? `Picture from ${photoSource}. Change it there and it updates here the next time you sign in.`
              : "Your picture is picked for your account and costs nothing to store. Sign in with Google or GitHub to use your own photo instead."}
          </span>
        </div>
      </div>

      <form onSubmit={save} className="prof__form">
        <div className="prof__field">
          <label htmlFor="prof-name">{t("pch.authDisplayName")}</label>
          <Input
            id="prof-name"
            value={displayName}
            maxLength={80}
            autoComplete="name"
            disabled={busy}
            placeholder="Shown on the leaderboard and on certificates"
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>

        {/* The button appears when there is something to save, so the form is
            never a row of controls waiting to be used. */}
        {dirty ? (
          <Button
            type="submit"
            size="sm"
            disabled={busy}
            className="prof__save"
          >
            {busy ? "Saving…" : "Save name"}
          </Button>
        ) : null}
      </form>

      <div className="prof__rows">
        <div className="prof__row">
          <span className="prof__row-label">{t("pch.authEmail")}</span>
          <span className="prof__row-value">
            {user.email}
            {user.emailVerified ? (
              <span className="prof__verified">
                <BadgeCheck className="size-3.5" aria-hidden="true" />
                verified
              </span>
            ) : null}
          </span>
          {user.emailVerified ? null : (
            <Button
              variant="outline"
              size="sm"
              disabled={sending}
              onClick={() => void verify()}
            >
              Send verification email
            </Button>
          )}
        </div>

        <div className="prof__row">
          <span className="prof__row-label">Last signed in</span>
          <span className="prof__row-value">{lastSeen}</span>
        </div>

        <div className="prof__row">
          <span className="prof__row-label">{t("pch.authSignedInWith")}</span>
          <span className="prof__row-value prof__providers">
            {user.providerData.map((p) => {
              const Icon = PROVIDER_ICONS[p.providerId] ?? Mail;
              return (
                <span className="prof__provider" key={p.providerId}>
                  <Icon className="size-3.5" />
                  {PROVIDER_LABELS[p.providerId] ?? p.providerId}
                </span>
              );
            })}
          </span>
          {hasPassword ? (
            <Button
              variant="outline"
              size="sm"
              disabled={sending}
              onClick={() => void resetPassword()}
            >
              Change password
            </Button>
          ) : null}
        </div>
      </div>
    </section>
  );
}

/* -------------------------------------------------------------------------- */
/* Preferences                                                                 */
/* -------------------------------------------------------------------------- */

function Preferences({
  user,
  onStatus,
}: {
  user: User;
  onStatus: (status: Status | null) => void;
}) {
  const [prefs, setPrefs] = useState<Prefs | null>(null);
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      try {
        const { doc, getDoc } = await import("firebase/firestore");
        const { getDb } = await import("@/src/lib/firebase/client");
        const db = await getDb();
        const snapshot = await getDoc(doc(db, "users", user.uid));
        if (!cancelled) setPrefs((snapshot.data()?.settings ?? {}) as Prefs);
      } catch {
        if (!cancelled) setPrefs({});
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [user.uid]);

  async function toggle(key: string, on: boolean) {
    if (!prefs) return;
    setSaving(key);
    onStatus(null);

    try {
      const { doc, setDoc } = await import("firebase/firestore");
      const { getDb } = await import("@/src/lib/firebase/client");
      const db = await getDb();

      // Only this switch's key is written, and state updates functionally.
      // Spreading the `prefs` captured by this call wrote the whole settings
      // map as it was a moment ago -- so flipping a second switch before the
      // first save returned put the first one back.
      await setDoc(
        doc(db, "users", user.uid),
        { uid: user.uid, settings: { [key]: on } },
        { merge: true },
      );
      setPrefs((current) => ({ ...(current ?? {}), [key]: on }));

      // The leaderboard row is derived from server-side records, so ask the
      // function to recompute rather than writing a row here. Opting out
      // deletes the row, which is the same call.
      if (key === "leaderboard") {
        const { callApi } = await import("@/src/lib/firebase/client");
        await callApi("publish-leaderboard");
      }

      onStatus({ text: t("pch.authSaved"), tone: "success" });
    } catch (err) {
      onStatus({ text: await errorMessage(err), tone: "error" });
    } finally {
      setSaving(null);
    }
  }

  const rows = [
    {
      key: "leaderboard",
      label: t("pch.prefLeaderboard"),
      hint: t("pch.prefLeaderboardHint"),
    },
    {
      key: "digest",
      label: t("pch.prefDigest"),
      hint: t("pch.prefDigestHint"),
    },
  ];

  return (
    <section className="prof__block" aria-labelledby="prof-prefs">
      <h2 id="prof-prefs" className="prof__h2">
        {t("pch.prefsTitle")}
      </h2>

      <div className="prof__rows">
        {rows.map((row) => (
          <label className="prof__row prof__row--switch" key={row.key}>
            <span className="prof__row-label">{row.label}</span>
            <span className="prof__row-hint">{row.hint}</span>
            <Switch
              checked={prefs?.[row.key] === true}
              disabled={prefs === null || saving === row.key}
              onCheckedChange={(on) => void toggle(row.key, on)}
            />
          </label>
        ))}
      </div>
    </section>
  );
}

/* -------------------------------------------------------------------------- */
/* Data                                                                        */
/* -------------------------------------------------------------------------- */

function YourData({ onStatus }: { onStatus: (status: Status | null) => void }) {
  const [busy, setBusy] = useState(false);

  /**
   * Hand the learner everything the site holds about them, as one JSON file.
   *
   * Built in the browser from their own records rather than emailed or
   * queued: there is nothing here the account cannot already read.
   */
  async function exportData() {
    setBusy(true);
    onStatus(null);
    try {
      const { exportUserData } = await import("@/src/lib/firebase/auth");
      const data = await exportUserData();
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${SITE_SLUG}-data.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      onStatus({ text: await errorMessage(err), tone: "error" });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="prof__block" aria-labelledby="prof-data">
      <h2 id="prof-data" className="prof__h2">
        Your data
      </h2>

      <div className="prof__rows">
        <div className="prof__row">
          <span className="prof__row-label">Everything we store</span>
          <span className="prof__row-hint">
            Your account details, progress, quiz results, bookmarks and notes,
            as one JSON file.
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={busy}
            onClick={() => void exportData()}
          >
            <Download className="size-4" aria-hidden="true" />
            {busy ? "Preparing…" : "Download"}
          </Button>
        </div>
      </div>
    </section>
  );
}

/* -------------------------------------------------------------------------- */
/* Deletion                                                                    */
/* -------------------------------------------------------------------------- */

/**
 * The button stays disabled until the confirmation word is typed exactly.
 * This cannot be undone, so it takes a deliberate action rather than a single
 * stray click.
 */
function DangerZone({
  onStatus,
}: {
  onStatus: (status: Status | null) => void;
}) {
  const [open, setOpen] = useState(false);
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);

  async function remove() {
    setBusy(true);
    onStatus(null);
    try {
      const { deleteAccount } = await import("@/src/lib/firebase/auth");
      await deleteAccount();
      onStatus({ text: t("pch.authDeleted"), tone: "success" });
      window.setTimeout(() => {
        window.location.href = "/";
      }, 1500);
    } catch (err) {
      onStatus({ text: await errorMessage(err), tone: "error" });
      setBusy(false);
    }
  }

  return (
    <section className="prof__danger" aria-labelledby="prof-danger">
      <h2 id="prof-danger" className="prof__h2 prof__h2--danger">
        <ShieldAlert className="size-4" aria-hidden="true" />
        {t("pch.authDelete")}
      </h2>

      <p className="prof__row-hint">{t("pch.authDeleteWarn")}</p>

      {open ? (
        <div className="prof__confirm">
          <div className="prof__field">
            <label htmlFor="prof-delete">{t("pch.authDeleteConfirm")}</label>
            <Input
              id="prof-delete"
              autoComplete="off"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
            />
          </div>

          <div className="prof__confirm-actions">
            <Button
              variant="destructive"
              size="sm"
              disabled={busy || confirm.trim() !== "DELETE"}
              onClick={() => void remove()}
            >
              {busy ? "Deleting…" : "Delete my account"}
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Keep my account
            </Button>
          </div>
        </div>
      ) : (
        <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
          {t("pch.authDelete")}
        </Button>
      )}
    </section>
  );
}

export default ProfilePanel;
