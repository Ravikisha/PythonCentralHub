"use client";

/**
 * Runs exercise code in /scripts/exercise-worker.js and hands back the output
 * and, on Submit, the grade.
 *
 * One worker for the whole page, started on the first Run. A run that goes
 * past the time limit -- an infinite loop, a `while True` waiting for input
 * -- terminates the worker, and the next run starts a new one. Loading
 * Python and its packages is not timed: on a slow connection the first run
 * can take a while, and that is not the learner's code misbehaving.
 */

export interface Grade {
  passed: boolean;
  message: string;
}

export interface RunResult {
  stdout: string;
  error: string | null;
  grade: Grade | null;
  timedOut?: boolean;
  /** Something about how this run differs from a normal computer. */
  notice?: string | null;
}

export type RunStatus = "loading" | "packages" | "running";

const TIME_LIMIT_MS = 30_000;

interface Pending {
  resolve: (result: RunResult) => void;
  onStatus?: (status: RunStatus) => void;
  timer?: number;
}

let worker: Worker | null = null;
let seq = 0;
const pending = new Map<number, Pending>();

function reset(reason: RunResult) {
  worker?.terminate();
  worker = null;
  for (const [, job] of pending) {
    window.clearTimeout(job.timer);
    job.resolve(reason);
  }
  pending.clear();
}

function getWorker(): Worker {
  if (worker) return worker;
  worker = new Worker("/scripts/exercise-worker.js");
  worker.onmessage = (event: MessageEvent) => {
    const data = event.data as { id: number; status?: RunStatus } & Partial<RunResult>;
    const job = pending.get(data.id);
    if (!job) return;

    if (data.status) {
      job.onStatus?.(data.status);
      if (data.status === "running") {
        job.timer = window.setTimeout(() => {
          reset({
            stdout: "",
            error: `Stopped after ${TIME_LIMIT_MS / 1000} seconds. Look for a loop that never ends.`,
            grade: null,
            timedOut: true,
          });
        }, TIME_LIMIT_MS);
      }
      return;
    }

    window.clearTimeout(job.timer);
    pending.delete(data.id);
    job.resolve({
      stdout: data.stdout ?? "",
      error: data.error ?? null,
      grade: data.grade ?? null,
      notice: data.notice ?? null,
    });
  };
  worker.onerror = (event) => {
    // A crashed runner is ours to fix, not the learner's: report it.
    void import("@/lib/report-error").then(({ reportError }) =>
      reportError(event.message || "exercise worker crashed", "exercise-runner"),
    );
    reset({ stdout: "", error: "Python stopped unexpectedly. Run again.", grade: null });
  };
  return worker;
}

export function runExercise(
  job: { pre?: string; code: string; sct?: string | null },
  onStatus?: (status: RunStatus) => void,
): Promise<RunResult> {
  const id = ++seq;
  return new Promise((resolve) => {
    pending.set(id, { resolve, onStatus });
    getWorker().postMessage({
      id,
      pre: job.pre ?? "",
      code: job.code,
      sct: job.sct ?? null,
    });
  });
}
