/**
 * shadcn/ui class-merge helper, for the ported aceternity/magicui components
 * that import `@/lib/utils`.
 *
 * Re-exported from the `cn` package the shadcn primitives in components/ui
 * already use, so the site has one implementation instead of two (this file
 * used to build its own from clsx + tailwind-merge).
 */
export { cn } from "cn";
