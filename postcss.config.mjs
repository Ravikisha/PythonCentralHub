/**
 * Tailwind v4 for Next.
 *
 * The Astro build used `@tailwindcss/vite`; Next's pipeline is PostCSS, so the
 * same Tailwind version is wired through its PostCSS plugin instead. Both can
 * coexist while the migration runs -- they read the same `@theme` block in
 * app/globals.css.
 */
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
