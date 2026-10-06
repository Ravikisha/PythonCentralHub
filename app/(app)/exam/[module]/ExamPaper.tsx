"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { StatusLine, type Status } from "@/components/auth/StatusLine";
import { messageFor } from "@/components/auth/session";
import { t } from "@/lib/strings";

interface ExamDoc {
  title: string;
  passScore: number;
  questions: { q: string; options: string[] }[];
}

interface Grade {
  score: number;
  passScore: number;
  passed: boolean;
  correct: number;
  total: number;
  /** Filled only on a pass. A fail returns the score alone, so retries
      cannot be used to work out the key. */
  explanations: string[];
}

/** What is blocking the paper, if anything. */
type Gate =
  | { kind: "checking" }
  | { kind: "sign-in" }
  | { kind: "verify" }
  | { kind: "missing" }
  | { kind: "failed"; message: string }
  | { kind: "open"; exam: ExamDoc };

export function ExamPaper({ module }: { module: string }) {
  const [gate, setGate] = useState<Gate>({ kind: "checking" });
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [grade, setGrade] = useState<Grade | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [busy, setBusy] = useState(false);
  const resultRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      // All of it inside the try: offline, `currentUser()` or `reload()`
      // rejected outside it and the page sat on "Loading" for good.
      try {
        const { currentUser } = await import("@/src/lib/firebase/auth");
        const user = await currentUser();

        // Both gates exist server-side too, in `requireVerifiedCaller`. These
        // are here so the learner is told why before sitting a paper that
        // would be refused at grading time.
        if (!user || user.isAnonymous) {
          if (!cancelled) setGate({ kind: "sign-in" });
          return;
        }

        await user.reload();
        if (!user.emailVerified) {
          if (!cancelled) setGate({ kind: "verify" });
          return;
        }

        const { doc, getDoc } = await import("firebase/firestore");
        const { getDb } = await import("@/src/lib/firebase/client");
        const snap = await getDoc(doc(await getDb(), "exams", module));

        if (cancelled) return;
        setGate(
          snap.exists()
            ? { kind: "open", exam: snap.data() as ExamDoc }
            : { kind: "missing" },
        );
      } catch (err) {
        console.error("[exam] load failed:", err);
        if (!cancelled) {
          setGate({
            kind: "failed",
            message: messageFor("pch.authErrGeneric"),
          });
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [module]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (gate.kind !== "open") return;
    setStatus(null);

    const picked: number[] = [];
    for (let i = 0; i < gate.exam.questions.length; i += 1) {
      if (answers[i] === undefined) {
        setStatus({ text: t("pch.examUnanswered"), tone: "error" });
        return;
      }
      picked.push(answers[i]);
    }

    setBusy(true);
    setStatus({ text: t("pch.examGrading"), tone: "info" });

    try {
      const { callApi } = await import("@/src/lib/firebase/client");
      const result = await callApi<Grade>("grade-exam", {
        module,
        answers: picked,
      });
      setGrade(result);
      setStatus(null);
      // Released here too, not only on failure: the claim button below shares
      // this flag and stayed disabled after every pass.
      setBusy(false);
      // The paper stays on screen above the result, so bring the mark into
      // view rather than leaving the reader at the last question.
      window.requestAnimationFrame(() =>
        resultRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "nearest",
        }),
      );
    } catch (err) {
      const message = (err as { message?: string }).message;
      setStatus({
        text: message || messageFor("pch.authErrGeneric"),
        tone: "error",
      });
      setBusy(false);
    }
  }

  async function claim() {
    setBusy(true);
    setStatus(null);
    try {
      const { callApi } = await import("@/src/lib/firebase/client");
      const { certificateId } = await callApi<{ certificateId: string }>(
        "issue-certificate",
        {
          module,
        },
      );
      setStatus({ text: t("pch.examIssued"), tone: "success" });
      window.location.href = `/certificates/?new=${certificateId}`;
    } catch (err) {
      // The server refuses with a readable reason -- "Complete 154 of 171
      // pages first" -- which is more use than a generic failure.
      const message = (err as { message?: string }).message;
      setStatus({
        text: message || messageFor("pch.authErrGeneric"),
        tone: "error",
      });
      setBusy(false);
    }
  }

  if (gate.kind === "checking")
    return <p className="app__loading">{t("pch.examLoading")}</p>;
  if (gate.kind === "missing")
    return <p className="pch-auth__intro">{t("pch.examMissing")}</p>;
  if (gate.kind === "failed")
    return <p className="pch-auth__intro">{gate.message}</p>;

  if (gate.kind === "sign-in" || gate.kind === "verify") {
    const signIn = gate.kind === "sign-in";
    return (
      <div className="app__gate">
        <p>{signIn ? t("pch.examSignIn") : t("pch.examVerify")}</p>
        <p className="app__gate-actions">
          <Link
            className="pch-auth__submit app__gate-primary"
            href={signIn ? `/login/?next=/exam/${module}/` : "/verify-email/"}
          >
            {signIn ? t("pch.authSignIn") : t("pch.authVerifyTitle")}
          </Link>
          {signIn ? (
            <Link
              className="pch-auth__secondary"
              href={`/signup/?next=/exam/${module}/`}
            >
              {t("pch.authCreateAccount")}
            </Link>
          ) : null}
        </p>
      </div>
    );
  }

  return (
    <>
      {grade === null ? (
        <form onSubmit={submit} noValidate>
          <ol className="pch-exam__list">
            {gate.exam.questions.map((question, qi) => (
              <li className="pch-exam__item" key={qi} data-index={qi}>
                {/* Question text is author-written prose but arrives from the
                    database, so it renders as text, never as HTML. */}
                <p className="pch-exam__q">{question.q}</p>

                {question.options.map((option, oi) => (
                  <label
                    className="pch-exam__option"
                    key={oi}
                    htmlFor={`q${qi}o${oi}`}
                  >
                    <input
                      type="radio"
                      name={`q${qi}`}
                      id={`q${qi}o${oi}`}
                      value={oi}
                      checked={answers[qi] === oi}
                      onChange={() => setAnswers({ ...answers, [qi]: oi })}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </li>
            ))}
          </ol>

          <button type="submit" className="pch-auth__submit" disabled={busy}>
            {t("pch.examSubmit")}
          </button>
        </form>
      ) : (
        <ol className="pch-exam__list">
          {gate.exam.questions.map((question, qi) => (
            <li className="pch-exam__item" key={qi}>
              <p className="pch-exam__q">{question.q}</p>

              {question.options.map((option, oi) => (
                <span
                  className="pch-exam__option"
                  key={oi}
                  data-picked={String(answers[qi] === oi)}
                >
                  <input
                    type="radio"
                    checked={answers[qi] === oi}
                    readOnly
                    disabled
                  />
                  <span>{option}</span>
                </span>
              ))}

              {/* Explanations only come back on a pass; on a fail the array is
                  empty by design, so there is nothing to reveal. */}
              {grade.explanations[qi] ? (
                <p className="pch-exam__explain">{grade.explanations[qi]}</p>
              ) : null}
            </li>
          ))}
        </ol>
      )}

      <StatusLine status={status} />

      {grade ? (
        <section
          className="pch-exam__result"
          data-passed={String(grade.passed)}
          ref={resultRef}
        >
          <p className="pch-exam__score">
            <strong>{grade.score}</strong>
            <span>%</span>
          </p>
          <p>{grade.passed ? t("pch.examPassed") : t("pch.examFailed")}</p>

          <p className="pch-dash__actions">
            {grade.passed ? (
              <button
                type="button"
                className="pch-auth__submit"
                disabled={busy}
                onClick={() => void claim()}
              >
                {t("pch.examClaim")}
              </button>
            ) : (
              <button
                type="button"
                className="pch-auth__secondary"
                onClick={() => window.location.reload()}
              >
                {t("pch.examRetry")}
              </button>
            )}
          </p>
        </section>
      ) : null}
    </>
  );
}

export default ExamPaper;
