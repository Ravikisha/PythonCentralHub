// Upload exams, answer keys and module page counts to Firestore.
//
//   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json \
//     node scripts/seed-exams.mjs [--dry]
//
// Reads every src/data/exams/*.yaml and splits each one in two:
//
//   exams/{module}     title, pass mark, and the questions WITHOUT answers
//   examKeys/{module}  the answer indexes and explanations, readable by nobody
//
// The split is the whole point. `exams/*` is client-readable so the paper can
// be rendered; if the answers travelled with it, "server-graded" would mean
// nothing -- anyone could read the key out of the network tab. Explanations
// ride with the key rather than the paper because they frequently state the
// correct answer; `gradeExam` releases them only once the learner has passed.
//
// Also writes config/modules, the page-count denominator `issueCertificate`
// checks completion against. It comes from public/progress-manifest.json, so
// run `npm run progress:manifest` first (a plain `npm run build` does it).
//
// Needs a service account key: Firebase console -> Project settings ->
// Service accounts -> Generate new private key. Keep it out of the repo;
// .gitignore already covers *.json only under specific paths, so store it
// outside the working tree.
import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import yaml from "js-yaml";
// firebase-admin is imported further down, after the --dry exit: validating a
// question bank should need no credentials and no server SDK installed.

const EXAM_DIR = "src/data/exams";
const MANIFEST = "public/progress-manifest.json";
const DRY = process.argv.includes("--dry");

/* ---- load and validate ---------------------------------------------------- */

function loadExam(file) {
  const raw = yaml.load(readFileSync(join(EXAM_DIR, file), "utf8"));
  const where = `${EXAM_DIR}/${file}`;

  if (!raw?.module) throw new Error(`${where}: missing "module"`);
  if (!Array.isArray(raw.questions) || !raw.questions.length) {
    throw new Error(`${where}: needs at least one question`);
  }

  raw.questions.forEach((q, i) => {
    const at = `${where} q${i + 1}`;
    if (typeof q.q !== "string" || !q.q.trim()) throw new Error(`${at}: empty question`);
    if (!Array.isArray(q.options) || q.options.length < 2) {
      throw new Error(`${at}: needs at least two options`);
    }
    if (!Number.isInteger(q.answer) || q.answer < 0 || q.answer >= q.options.length) {
      throw new Error(`${at}: "answer" must index into options`);
    }
  });

  return raw;
}

const files = existsSync(EXAM_DIR)
  ? readdirSync(EXAM_DIR).filter((f) => /\.ya?ml$/.test(f))
  : [];

if (!files.length) {
  console.error(`No exams found in ${EXAM_DIR}/`);
  process.exit(1);
}

const exams = files.map(loadExam);

if (!existsSync(MANIFEST)) {
  console.error(`${MANIFEST} is missing — run: npm run progress:manifest`);
  process.exit(1);
}
const manifest = JSON.parse(readFileSync(MANIFEST, "utf8"));
const counts = Object.fromEntries(manifest.modules.map((m) => [m.slug, m.count]));

for (const exam of exams) {
  if (!counts[exam.module]) {
    throw new Error(
      `${exam.module}: no such module in ${MANIFEST} — certificates would be un-issuable`
    );
  }
}

/* ---- report --------------------------------------------------------------- */

for (const exam of exams) {
  console.log(
    `${exam.module.padEnd(32)} ${String(exam.questions.length).padStart(3)} question(s), ` +
      `pass ${exam.passScore ?? 70}%, ${counts[exam.module]} pages`
  );
}
console.log(`config/modules: ${Object.keys(counts).length} module count(s)`);

if (DRY) {
  console.log("\n--dry: nothing written.");
  process.exit(0);
}

/* ---- upload --------------------------------------------------------------- */

const { initializeApp, cert, applicationDefault } = await import("firebase-admin/app");
const { getFirestore } = await import("firebase-admin/firestore");

const keyPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
initializeApp({
  credential: keyPath ? cert(JSON.parse(readFileSync(keyPath, "utf8"))) : applicationDefault(),
  projectId: process.env.FIREBASE_PROJECT_ID || "pythoncentralhub",
});

const db = getFirestore();
const batch = db.batch();

for (const exam of exams) {
  batch.set(db.doc(`exams/${exam.module}`), {
    module: exam.module,
    title: exam.title ?? exam.module,
    passScore: exam.passScore ?? 70,
    timeLimitMinutes: exam.timeLimitMinutes ?? null,
    // Answers and explanations deliberately absent.
    questions: exam.questions.map((q) => ({ q: q.q, options: q.options })),
    updatedAt: new Date().toISOString(),
  });

  batch.set(db.doc(`examKeys/${exam.module}`), {
    module: exam.module,
    answers: exam.questions.map((q) => q.answer),
    explanations: exam.questions.map((q) => q.explain ?? ""),
    updatedAt: new Date().toISOString(),
  });
}

batch.set(db.doc("config/modules"), { counts, updatedAt: new Date().toISOString() });

await batch.commit();
console.log(`\nUploaded ${exams.length} exam(s) and the module counts.`);
