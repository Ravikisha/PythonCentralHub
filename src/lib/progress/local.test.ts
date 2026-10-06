// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from "vitest";
import {
  enrol,
  exercisesByPage,
  read,
  recordExercise,
  recordQuiz,
  setComplete,
  unenrol,
} from "./local";
import { practiceIn } from "@/components/courses/useProgress";

beforeEach(() => localStorage.clear());

describe("progress store", () => {
  it("finishing a lesson enrols the learner in its course", () => {
    setComplete("tutorials/numbers", true);
    const state = read();
    expect(state.modules.tutorials).toEqual(["tutorials/numbers"]);
    expect(state.enrolled).toEqual(["tutorials"]);
  });

  it("removing a course keeps its progress", () => {
    enrol("machine-learning");
    setComplete("machine-learning/intro", true);
    unenrol("machine-learning");
    expect(read().enrolled).toEqual([]);
    expect(read().modules["machine-learning"]).toEqual(["machine-learning/intro"]);
  });

  it("keeps the first pass of an exercise only", () => {
    recordExercise("tutorials/lists", 0);
    const first = read().exercises?.["tutorials/lists#0"];
    recordExercise("tutorials/lists", 0);
    expect(read().exercises?.["tutorials/lists#0"]).toBe(first);
    recordExercise("tutorials/lists", 2);
    expect(exercisesByPage().get("tutorials/lists")).toBe(2);
  });

  it("keeps a quiz's best score", () => {
    recordQuiz("tutorials/lists", 0, 3, 4);
    recordQuiz("tutorials/lists", 0, 1, 4);
    expect(read().quizzes["tutorials/lists#0"].correct).toBe(3);
  });

  it("reads a store written before exercises existed", () => {
    localStorage.setItem(
      "pch-progress",
      JSON.stringify({ v: 1, modules: { tutorials: ["tutorials/a"] }, bookmarks: [], quizzes: {}, notes: {}, streak: { last: "", count: 0, longest: 0 }, hydrated: false }),
    );
    expect(read().exercises).toEqual({});
    expect(read().enrolled).toEqual(["tutorials"]);
  });
});

describe("practiceIn", () => {
  it("caps passes at each lesson's exercise count", () => {
    const lessons = [
      { url: "/tutorials/lists/", exercises: 2 },
      { url: "/tutorials/sets/", exercises: 3 },
    ];
    const summary = practiceIn(lessons, {
      exercises: new Map([["tutorials/lists", 5]]),
      quizzes: new Map([["tutorials/sets", { correct: 3, total: 4 }]]),
    });
    expect(summary).toEqual({ passed: 2, exercises: 5, quizCorrect: 3, quizTotal: 4, quizzesTaken: 1 });
  });
});
