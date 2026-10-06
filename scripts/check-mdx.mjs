// Parse MDX files the way the build will, without running the build.
//
//   node scripts/check-mdx.mjs <file.mdx> [more files...]
//   node scripts/check-mdx.mjs --all
//
// A full build takes minutes; a stray backtick or `${` inside a
// DataCampExercise prop breaks the page it is in and nothing else, and this
// finds it in a second. It also checks each exercise has what grading needs:
// sample code, a solution and an sct.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { compile } from "@mdx-js/mdx";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import remarkDirective from "remark-directive";
import { visit } from "unist-util-visit";

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (/\.mdx$/.test(entry)) out.push(p);
  }
  return out;
}

const args = process.argv.slice(2);
const files = args.includes("--all") ? walk("src/content/docs") : args;
if (!files.length) {
  console.error("usage: node scripts/check-mdx.mjs <file.mdx>... | --all");
  process.exit(2);
}

/** Front matter is YAML, not MDX: blank it, keeping line numbers. */
function withoutFrontMatter(source) {
  if (!source.startsWith("---")) return source;
  const end = source.indexOf("\n---", 3);
  if (end === -1) return source;
  const cut = end + 4;
  return source.slice(0, cut).replace(/[^\n]/g, "") + source.slice(cut);
}

let failed = 0;
for (const file of files) {
  const source = readFileSync(file, "utf8");
  const problems = [];

  // `{name}` in prose is a JavaScript expression in MDX. Lessons define no
  // variables, so a bare name compiles fine and then throws "name is not
  // defined" while the page is rendered -- usually LaTeX written as \[ ... \]
  // or 	ext{...} outside $...$, which MDX reads as braces.
  const bareExpressions = () => (tree) => {
    visit(tree, ["mdxFlowExpression", "mdxTextExpression"], (node) => {
      const value = String(node.value ?? "").trim();
      if (/^[A-Za-z_$][\w$]*(\.[A-Za-z_$][\w$]*)*$/.test(value)) {
        problems.push(
          `line ${node.position?.start.line}: {${value}} is read as a JavaScript variable and will fail at render; put maths in $...$ or escape the braces`,
        );
      }
    });
  };

  try {
    await compile(withoutFrontMatter(source), {
      remarkPlugins: [remarkGfm, remarkMath, remarkDirective, bareExpressions],
    });
  } catch (err) {
    problems.push(`does not compile: ${String(err.message).split("\n")[0]}`);
  }

  // Components are provided to every page (mdx-components.tsx); an import of
  // an Astro file compiles here but fails the Next build.
  for (const m of source.matchAll(/^import .*\.astro["'];?\s*$/gm)) {
    const line = source.slice(0, m.index).split("\n").length;
    problems.push(`line ${line}: imports an Astro component; remove the import`);
  }

  for (const m of source.matchAll(/<DataCampExercise\b([\s\S]*?)\/>/g)) {
    const props = m[1];
    const line = source.slice(0, m.index).split("\n").length;
    for (const need of ["code", "solution", "sct"]) {
      if (!new RegExp(`\\b${need}=\\{`).test(props)) {
        problems.push(`line ${line}: exercise has no ${need}`);
      }
    }
  }

  if (problems.length) {
    failed += 1;
    console.log(`FAIL ${file}`);
    for (const p of problems) console.log(`  - ${p}`);
  } else if (!args.includes("--all")) {
    console.log(`ok   ${file}`);
  }
}
console.log(`\n${files.length - failed}/${files.length} file(s) pass.`);
process.exitCode = failed ? 1 : 0;
