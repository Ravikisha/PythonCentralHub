import { readFile } from "node:fs/promises";
import { codeToHtml } from "shiki";
import { SiGithub } from "@icons-pack/react-simple-icons";
import { REPO_URL } from "@/lib/site";

/**
 * FileCode — a real file from the repo, highlighted and collapsible.
 *
 * Reads the file at build time and highlights it with Shiki, reproducing the
 * exact attributes the site's CSS keys off: the `data-rehype-pretty-code-*`
 * panel wrapper and `[data-line]` spans that drive the line-number counter.
 * The Astro version did this through `astro:components`; here Shiki is called
 * directly, which is what that component was wrapping anyway.
 *
 * Async server component: the filesystem read and the highlighting both happen
 * on the server, and the 203 pages using it ship no client JS for it.
 */
export interface FileCodeProps {
  /** Repo-relative path, e.g. `src/lib/progress/local.ts`. */
  file: string;
  lang?: string;
  title?: string;
  /** Shiki meta string, e.g. a line-highlight range. */
  meta?: string;
  open?: boolean;
}

const GITHUB_BLOB = `${REPO_URL}/blob/main`;

export async function FileCode({
  file,
  lang = "python",
  title,
  open = true,
}: FileCodeProps) {
  const fileExtension = file.split(".").pop() ?? "python";

  let code: string;
  try {
    code = (await readFile(file, "utf-8")).replace(/\s+$/, "");
  } catch {
    // A missing file used to fail the whole Astro build. Failing one block is
    // a better trade at 1190 pages: the page still renders and the gap is
    // visible to whoever is reading it.
    return (
      <div className="pch-filecode pch-filecode--missing">
        <p>File not found: {file}</p>
      </div>
    );
  }

  const maxDigits = String(code.split("\n").length).length;

  const html = await codeToHtml(code, {
    lang,
    themes: { light: "github-light", dark: "github-dark-dimmed" },
    defaultColor: false,
    transformers: [
      {
        name: "pch-pretty-code-shape",
        code(node) {
          node.properties["data-language"] = lang;
          node.properties["data-line-numbers"] = "";
          node.properties["data-line-numbers-max-digits"] = String(maxDigits);
        },
        line(node) {
          node.properties["data-line"] = "";
        },
      },
    ],
  });

  return (
    <details className="pch-filecode" open={open}>
      <summary>
        <span className="pch-fc-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <span className="pch-fc-name">{title ?? fileExtension}</span>
      </summary>

      <a
        className="pch-fc-gh"
        href={`${GITHUB_BLOB}/${file}`}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="View this file on GitHub"
      >
        <SiGithub className="size-[0.95em]" aria-hidden="true" />
        <span>Source</span>
      </a>

      <figure data-rehype-pretty-code-figure="">
        <figcaption data-rehype-pretty-code-title="" data-language={lang}>
          {title ?? fileExtension}
        </figcaption>
        {/* Shiki's output is generated here on the server from a file in this
            repo, not from user input. */}
        <div dangerouslySetInnerHTML={{ __html: html }} />
      </figure>
    </details>
  );
}

export default FileCode;
