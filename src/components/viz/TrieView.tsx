"use client";

/**
 * TrieView — step-through visualization of trie insertion and search.
 *
 * A trie is a tree whose edges carry characters, so this renders through
 * `TreeStage` with the edge-label support added for exactly this purpose. No new
 * renderer needed — recognising that is what kept the component count down.
 *
 * MDX usage:
 *
 *     import TrieView from "../../../../components/viz/TrieView.tsx";
 *
 *     <TrieView client:visible words={["cat", "car", "card", "dog"]} query="car"
 *       title="Common prefixes are stored once" />
 */
import { useMemo } from "react";
import VizPlayer from "./VizPlayer";
import { TreeStage } from "./TreeWalker";
import type { Frame } from "./frames";
import type { TreeState } from "./algos/trees";
import { TRIE_ALGOS, type TrieInput } from "./algos/structures";

export interface TrieViewProps extends TrieInput {
  /** Registry key. Only `insert-search` exists so far, and it is the default. */
  algo?: string;
  title: string;
  desc?: string;
  lib?: string;
  showCode?: boolean;
  ms?: number;
  autoPlay?: boolean;
}

export default function TrieView({
  algo = "insert-search",
  title,
  desc,
  lib,
  showCode = true,
  ms,
  autoPlay,
  ...input
}: TrieViewProps) {
  const trace = useMemo(() => {
    const fn = TRIE_ALGOS[algo];
    if (!fn) return { frames: [] as Frame<TreeState>[] };
    return fn(input as TrieInput);
  }, [algo, JSON.stringify(input.words), input.query]);

  if (!TRIE_ALGOS[algo]) {
    return (
      <div className="pch-viz pch-vz">
        <div className="pch-viz__bar">
          <span className="pch-viz__tag pch-vz__tag--trie">trie</span>
          <span className="pch-viz__title">{title}</span>
        </div>
        <p className="pch-vz__error">
          Unknown TrieView algo <code>{algo}</code>. Known keys: {Object.keys(TRIE_ALGOS).join(", ")}.
        </p>
      </div>
    );
  }

  return (
    <VizPlayer<TreeState>
      frames={trace.frames}
      code={showCode ? trace.code : undefined}
      result={trace.result}
      title={title}
      tag="trie"
      lib={lib ?? "prefix tree"}
      desc={desc}
      ms={ms}
      autoPlay={autoPlay}
      renderStage={(f) => <TreeStage state={f.state} />}
    />
  );
}
