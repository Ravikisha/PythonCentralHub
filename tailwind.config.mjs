import starlightPlugin from '@astrojs/starlight-tailwind';

// Generated color palettes — Python-blue accent (was generic tan).
// Ramp keyed to Python's official blue (#4b8bbe); used site-wide by starlight-tailwind.
const accent = { 200: '#a9cdec', 600: '#1f6fb2', 900: '#0e3350', 950: '#0a2435' };
// Cool neutral gray tuned to pair with the github-dark-dimmed code theme (#0d1117).
const gray = { 100: '#f5f6f8', 200: '#eceef2', 300: '#c0c3ca', 400: '#888c97', 500: '#545862', 700: '#353842', 800: '#24272f', 900: '#161a20' };
// `primary` — Python-blue ramp for form controls (Contact/Feedback use bg/ring
// primary-*, which was previously undefined and rendered transparent).
const primary = {
  50: '#eff6fc', 100: '#d8ebf8', 200: '#b3d6f0', 300: '#86bce6', 400: '#5a9fd8',
  500: '#3d86c6', 600: '#2f6ea8', 700: '#285d8c', 800: '#234d73', 900: '#1e3f5e',
};

/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		fontFamily:{
			"poppins": ['Poppins', 'sans-serif'],
		},
		extend: {
			colors: { accent, gray, primary },
		},
	},
	plugins: [starlightPlugin()],
};