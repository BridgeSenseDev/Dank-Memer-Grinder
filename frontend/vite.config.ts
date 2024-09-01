import { purgeCss } from "vite-plugin-tailwind-purgecss";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
	server: {
		fs: {
			allow: ["."]
		}
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./")
		}
	},
	plugins: [sveltekit(), purgeCss()]
});
