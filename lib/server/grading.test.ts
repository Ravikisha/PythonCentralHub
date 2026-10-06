import { describe, expect, it } from "vitest";
import {
  certificateBlocker,
  cooldownRemaining,
  countReal,
  grade,
  lessonsNeeded,
  parseAnswers,
} from "./grading";

describe("parseAnswers", () => {
  it("accepts a list of option numbers", () => {
    expect(parseAnswers([0, 3, 1])).toEqual([0, 3, 1]);
  });
  it.each([
    ["not a list", "0,1"],
    ["a negative option", [0, -1]],
    ["a fraction", [0, 1.5]],
    ["an option past Z", [26]],
    ["a string inside", [0, "1"]],
    ["more than 200 answers", Array(201).fill(0)],
  ])("rejects %s", (_, value) => {
    expect(parseAnswers(value)).toBeNull();
  });
});

describe("grade", () => {
  it("scores and rounds to a whole percent", () => {
    expect(grade([0, 1, 2], [0, 1, 3], 70)).toEqual({
      correct: 2,
      total: 3,
      score: 67,
      passed: false,
    });
  });
  it("passes exactly at the pass mark", () => {
    expect(grade([1, 1, 1, 1, 1, 1, 1, 0, 0, 0], Array(10).fill(1), 70).passed).toBe(true);
  });
  it("never divides by zero", () => {
    expect(grade([], [], 70).score).toBe(0);
  });
});

describe("cooldownRemaining", () => {
  it("is positive inside the window and not after it", () => {
    expect(cooldownRemaining(1_000, 600_000, 2_000)).toBe(599_000);
    expect(cooldownRemaining(1_000, 600_000, 700_000)).toBeLessThanOrEqual(0);
  });
});

describe("countReal", () => {
  const real = new Set(["tutorials/numbers", "tutorials/lists"]);
  it("counts only real lessons, once each, ignoring case", () => {
    expect(
      countReal(real, ["tutorials/numbers", "TUTORIALS/Numbers", "tutorials/lists", "made/up", 7]),
    ).toBe(2);
  });
  it("is zero for an unknown course or a non-list", () => {
    expect(countReal(undefined, ["tutorials/numbers"])).toBe(0);
    expect(countReal(real, "tutorials/numbers")).toBe(0);
  });
});

describe("certificates", () => {
  const base = { total: 171, share: 0.9, assessmentPassed: false };

  it("needs 90% of lessons, rounded up", () => {
    expect(lessonsNeeded(171, 0.9)).toBe(154);
    expect(certificateBlocker({ ...base, kind: "completion", completed: 153 })).toBe(
      "Complete 154 of 171 lessons first.",
    );
  });
  it("issues a completion certificate on lessons alone", () => {
    expect(certificateBlocker({ ...base, kind: "completion", completed: 154 })).toBeNull();
  });
  it("needs a passed assessment for an assessment certificate", () => {
    expect(certificateBlocker({ ...base, kind: "assessment", completed: 171 })).toBe(
      "Pass the final assessment first.",
    );
    expect(
      certificateBlocker({ ...base, kind: "assessment", completed: 171, assessmentPassed: true }),
    ).toBeNull();
  });
  it("checks lessons before the assessment", () => {
    expect(
      certificateBlocker({ ...base, kind: "assessment", completed: 10, assessmentPassed: true }),
    ).toBe("Complete 154 of 171 lessons first.");
  });
});
