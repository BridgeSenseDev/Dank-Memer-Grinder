<script lang="ts">
	import "../../../app.css";
	import { onMount } from "svelte";
	import { Button } from "$lib/components/ui/button";
	import { Progress } from "$lib/components/ui/progress";
	import SvelteMarkdown from "svelte-marked";
	import { Theme } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/config";
	import { cfg } from "$lib/state.svelte";
	import { Events } from "@wailsio/runtime";
	import { Update } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";

	let theme = $state<Theme>();
	let isDownloading = $state(false);
	let downloadProgress = $state(0);
	let downloadStep = $state<string>("Preparing download");
	let downloadError = $state<string | null>(null);

	let currentVersion = $state("");
	let newVersion = $state("");
	let changelogs = $state<{ version: string; notes: string[] }[]>([]);

	let source = $state("");

	$effect(() => {
		if (cfg.c?.gui) {
			theme = cfg.c.gui.theme;
			setTheme(theme);
		}
	});

	function setTheme(theme: Theme) {
		let isDark = theme === "dark";
		if (theme === "system") {
			isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
		}

		const handleThemeChange = (e: MediaQueryListEvent) => {
			if (theme === "system") {
				isDark = e.matches;
				document.documentElement.classList.toggle("dark", isDark);
			}
		};

		if (theme === "system") {
			const darkModeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
			darkModeMediaQuery.addEventListener("change", handleThemeChange);

			handleThemeChange({
				matches: darkModeMediaQuery.matches,
				media: darkModeMediaQuery.media
			} as MediaQueryListEvent);
		} else {
			document.documentElement.classList.toggle("dark", theme === "dark");
		}
	}

	$effect(() => {
		if (changelogs.length > 0) {
			source = changelogs
				.map((entry) => `# ${entry.version}\n${entry.notes.map((note) => `- ${note}`).join("\n")}`)
				.join("\n\n");
		}
	});

	onMount(() => {
		Events.On(
			"updateChanges",
			(data: { data: [string, string, { version: string; changelog: string }[]] }) => {
				currentVersion = data.data[0];
				newVersion = data.data[1];

				changelogs = data.data[2].map((item) => ({
					version: item.version,
					notes: Array.isArray(item.changelog) ? item.changelog : [item.changelog]
				}));
			}
		);

		Events.On("downloadProgress", (data: { data: [progress: number] }) => {
			downloadProgress = data.data[0];
			if (data.data[0] < 100) {
				downloadStep = `Downloading... ${data.data[0]}%`;
			} else {
				downloadStep = "Download complete!";
			}
		});

		Events.On("updateFailed", (data: { data: [error: string] }) => {
			downloadError = "Update failed: " + data.data[0];
		});
	});

	function handleCancel() {
		window.location.href = "/#/";
	}

	async function handleUpdate() {
		try {
			isDownloading = true;
			downloadProgress = 0;
			downloadError = null;
			downloadStep = "Initializing update...";
			await Update();
		} catch (error: unknown) {
			if (error instanceof Error) {
				downloadError = `Error: ${error.message}`;
			}
			console.error("Download failed:", error);
		} finally {
			setTimeout(() => {
				isDownloading = false;
			}, 1000);
		}
	}
</script>

<div class="mx-auto flex h-screen max-w-2xl flex-col p-8">
	<div class="mb-8 text-center">
		<h1 class="mb-4 text-3xl font-bold">Update Available</h1>
		<div class="flex justify-center space-x-8">
			<p>
				Current Version:
				<span class="font-medium text-red-500">{currentVersion}</span>
			</p>
			<p>
				New Version:
				<span class="font-medium text-green-500">
					{newVersion}
				</span>
			</p>
		</div>
	</div>

	<div class="bg-card mb-8 flex flex-1 flex-col rounded-lg border p-4 shadow-sm">
		<span class="mb-2 text-2xl font-bold">Changelog</span>
		<div class="flex-1 overflow-y-auto">
			<div class="prose text-black dark:text-white">
				<SvelteMarkdown {source} />
			</div>
		</div>
	</div>

	{#if isDownloading || downloadError}
		<div class="mb-8 space-y-2">
			{#if isDownloading}
				<div class="flex justify-between">
					<span>{downloadStep}</span>
					<span>{downloadProgress}%</span>
				</div>
				<Progress value={downloadProgress} />
			{/if}
			{#if downloadError}
				<p class="text-md text-center text-red-500">{downloadError}</p>
			{/if}
		</div>
	{/if}

	<div class="flex justify-center space-x-4">
		<Button variant="destructive" onclick={handleCancel} disabled={isDownloading}>Cancel</Button>
		<Button onclick={handleUpdate} disabled={isDownloading}>
			{isDownloading ? "Downloading..." : "Update Now"}
		</Button>
	</div>
</div>
