import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig, searchForWorkspaceRoot } from "vite";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
	server: {
		fs: {
			allow: [
				// search up for workspace root
				searchForWorkspaceRoot(process.cwd()),
				// your custom rules
				"./bindings/*"
			]
		}
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./")
		}
	},
	plugins: [sveltekit(), tailwindcss()]
});
