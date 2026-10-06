"use client";

import { useEffect, useId, useState } from "react";

/**
 * Quiz — self-check multiple choice for tutorial pages.
 *
 * The answer stays hidden until the reader commits to an option, then the
 * explanation is revealed. Answering is final: the point is to find out
 * whether you knew it, which a second guess destroys.
 *
 * On finishing every question it dispatches `pch:quiz-complete`, which the
 * progress layer listens for. That contract is deliberate — announcing rather
 * than writing keeps this component free of any storage dependency, so it
 * still works on pages with no progress tracking.
 *
 * These scores are for the learner's own dashboard only. The answers are in
 * the page source, so they can never gate a certificate; the exams in
 * `api/grade-exam` are marked server-side for exactly that reason.
 */
export interface QuizQuestion {
  /** The question text. Plain text — keep it one sentence. */
  q: string;
  /** 2–5 answer options, plain text. */
  options: string[];
  /** Zero-based index of the correct option. */
  answer: number;
  /** Shown after the reader answers, whether right or wrong. */
  explain?: string;
}

export interface QuizProps {
  questions: QuizQuestion[];
  /** Heading shown in the panel bar. */
  title?: string;
}

export function Quiz({ questions, title = "Check yourself" }: QuizProps) {
  const id = useId();
  /** Chosen option per question; undefined until answered. */
  const [picked, setPicked] = useState<Record<number, number>>({});
  /**
   * Progressive enhancement, as the Astro version did it.
   *
   * The server-rendered markup includes a <details> answer key, and the
   * `--interactive` class that hides it is only added once this has mounted.
   * With JS unavailable the buttons do nothing, so without the fallback the
   * reader would be left with questions and no way to check them.
   */
  const [interactive, setInteractive] = useState(false);
  useEffect(() => setInteractive(true), []);

  const answered = Object.keys(picked).length;
  const correct = questions.reduce(
    (n, item, qi) => (picked[qi] === item.answer ? n + 1 : n),
    0,
  );

  function choose(qi: number, oi: number) {
    if (picked[qi] !== undefined) return; // answering is final

    const next = { ...picked, [qi]: oi };
    setPicked(next);

    if (Object.keys(next).length === questions.length) {
      const score = questions.reduce(
        (n, item, i) => (next[i] === item.answer ? n + 1 : n),
        0,
      );
      // Ordinal distinguishes several quizzes on one page. Read from the DOM
      // at dispatch time rather than passed in, so authors never have to
      // number their quizzes by hand.
      const all = Array.from(document.querySelectorAll(".pch-quiz"));
      const self = document.getElementById(id);
      document.dispatchEvent(
        new CustomEvent("pch:quiz-complete", {
          detail: {
            ordinal: Math.max(0, self ? all.indexOf(self) : 0),
            correct: score,
            total: questions.length,
          },
        }),
      );
    }
  }

  const state =
    answered < questions.length
      ? "partial"
      : correct === questions.length
        ? "perfect"
        : "done";

  return (
    <section
      className={`pch-quiz${interactive ? " pch-quiz--interactive" : ""}`}
      id={id}
      aria-label={title}
    >
      <div className="pch-viz__bar">
        <span className="pch-viz__tag">quiz</span>
        <span className="pch-viz__title">{title}</span>
        <span
          className="pch-quiz__score"
          data-quiz-score=""
          data-state={state}
          aria-live="polite"
        >
          {answered > 0 ? `${correct} / ${questions.length}` : ""}
        </span>
      </div>

      <ol className="pch-quiz__list">
        {questions.map((item, qi) => {
          const choice = picked[qi];
          const done = choice !== undefined;

          return (
            <li
              className="pch-quiz__item"
              key={qi}
              data-quiz-item=""
              data-done={String(done)}
            >
              <p className="pch-quiz__q">{item.q}</p>

              <div className="pch-quiz__options" role="group">
                {item.options.map((opt, oi) => (
                  <button
                    type="button"
                    className="pch-quiz__opt"
                    key={oi}
                    disabled={done}
                    onClick={() => choose(qi, oi)}
                    data-quiz-opt=""
                    data-index={oi}
                    data-correct={oi === item.answer ? "true" : "false"}
                    // Once answered, the chosen option is marked right or
                    // wrong and the correct one is always revealed.
                    data-state={
                      !done
                        ? undefined
                        : oi === item.answer
                          ? "correct"
                          : oi === choice
                            ? "wrong"
                            : undefined
                    }
                  >
                    <span className="pch-quiz__letter">
                      {String.fromCharCode(65 + oi)}
                    </span>
                    <span className="pch-quiz__text">{opt}</span>
                  </button>
                ))}
              </div>

              {item.explain ? (
                <p
                  className="pch-quiz__explain"
                  data-quiz-explain=""
                  hidden={!done}
                >
                  {item.explain}
                </p>
              ) : null}

              {/* No-JS fallback: hidden by .pch-quiz--interactive once mounted. */}
              <details className="pch-quiz__fallback">
                <summary>Show answer</summary>
                <p>
                  <strong>{String.fromCharCode(65 + item.answer)}</strong>
                  {" — "}
                  {item.options[item.answer]}
                  {item.explain ? ` — ${item.explain}` : ""}
                </p>
              </details>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

export default Quiz;
