import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Python Central Hub',
			social: {
				github: 'https://github.com/Ravikisha/PythonCentralHub.git',
				instagram: 'https://www.instagram.com/ravikishan.69',
				"x.com": 'https://twitter.com/@Ravikishan_',
				email: 'mailto:ravikishan63392@gmail.com',
				linkedin: 'https://www.linkedin.com/in/ravi-kishan-62ab51221/'
			},
			sidebar: [
				// {
				// 	label: 'Guides',
				// 	items: [
				// 		// Each item here is one entry in the navigation menu.
				// 		{ label: 'Example Guide', link: '/guides/example/' },
				// 	],
				// },
				{
					label: 'Guides',
					autogenerate: { directory: 'guides' },
				},
				{
					label: 'Tutorials',
					autogenerate: { directory: 'tutorials' },
				},
				{
					label: 'Projects',
					autogenerate: { directory: 'projects' },
				},
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
			],
			customCss: [
				'./src/styles/global.css',
			]
		}),
	],
});
