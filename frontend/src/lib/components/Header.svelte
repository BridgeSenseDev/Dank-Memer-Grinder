<script lang="ts">
	import { page } from "$app/state";
	import { Button } from "$lib/components/ui/button";
	import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
	import { cfg } from "$lib/state.svelte";
	import * as Select from "$lib/components/ui/select";
	import { Moon, Sun } from "svelte-radix";
	import { Theme } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/config";

	let theme = $state<Theme>();
	let sunClass = $state("");
	let moonClass = $state("");

	let title = $derived(
		(page.url.hash.split("#/")[1] || "logs")
			.split(" ")
			.map((word) => (word ? word.charAt(0).toUpperCase() + word.slice(1) : ""))
			.join(" ")
	);

	$effect(() => {
		if (cfg.c?.gui) {
			theme = cfg.c.gui.theme;
			setTheme(theme);
		}
	});

	function setTheme(theme: Theme) {
		if (!cfg.c) return;
		cfg.c.gui.theme = theme;

		let isDark = theme === "dark";
		if (theme === "system") {
			isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
		}
		sunClass = `h-[1.2rem] w-[1.2rem] transition-all ${
			isDark ? "rotate-90 scale-0" : "rotate-0 scale-100"
		}`;
		moonClass = `absolute h-[1.2rem] w-[1.2rem] transition-all ${
			isDark ? "rotate-0 scale-100" : "rotate-90 scale-0"
		}`;

		const handleThemeChange = (e: MediaQueryListEvent) => {
			if (theme === "system") {
				isDark = e.matches;

				sunClass = `h-[1.2rem] w-[1.2rem] transition-all ${
					isDark ? "rotate-90 scale-0" : "rotate-0 scale-100"
				}`;
				moonClass = `absolute h-[1.2rem] w-[1.2rem] transition-all ${
					isDark ? "rotate-0 scale-100" : "rotate-90 scale-0"
				}`;
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

	function toggleCommands(state: boolean) {
		if (!cfg.c) return;
		const commands = cfg.c.commands as unknown as Record<string, { state: boolean }>;
		for (let command in commands) {
			commands[command].state = state;
		}
	}
</script>

<div class="header-container border-border sticky top-0 z-30 flex w-full flex-row border-b">
	<!-- Frosted glass backdrop elements -->
	<div class="backdrop"></div>
	<div class="backdrop-edge"></div>

	<!-- Your original header content -->
	<div class="border-border flex h-14 max-w-48 items-center border-r-2 border-b px-2">
		<Select.Root type="single" disabled>
			<Select.Trigger class="w-[180px]">config.json</Select.Trigger>
			<Select.Content>
				<Select.Item value="test">Test</Select.Item>
			</Select.Content>
		</Select.Root>
	</div>
	<div class="flex w-full flex-row justify-between px-4">
		<h1 class="flex items-center">{title}</h1>
		{#if title === "Commands" || theme}
			<div class="flex flex-row items-center space-x-2">
				{#if title === "Commands"}
					<Button onclick={() => toggleCommands(true)}>Enable all</Button>
					<Button variant="destructive" onclick={() => toggleCommands(false)}>Disable all</Button>
				{/if}
				<DropdownMenu.Root>
					<DropdownMenu.Trigger>
						<Button variant="outline" size="icon">
							<Sun class={sunClass} />
							<Moon class={moonClass} />
							<span class="sr-only">Toggle theme</span>
						</Button>
					</DropdownMenu.Trigger>
					<DropdownMenu.Content align="end">
						<DropdownMenu.Item onclick={() => setTheme(Theme.Light)}>Light</DropdownMenu.Item>
						<DropdownMenu.Item onclick={() => setTheme(Theme.Dark)}>Dark</DropdownMenu.Item>
						<DropdownMenu.Item onclick={() => setTheme(Theme.System)}>System</DropdownMenu.Item>
					</DropdownMenu.Content>
				</DropdownMenu.Root>
			</div>
		{/if}
	</div>
</div>

<style>
	.header-container {
		--thickness: 4px;
		position: sticky;
		top: 0;
		/* Fallback for unsupported browsers - reduced opacity */
		background: hsl(0deg 0% 100% / 0.85);
	}

	/* For dark mode support */
	:global(.dark) .header-container {
		background: hsl(220deg 10% 10% / 0.85);
	}

	/* Support for backdrop-filter browsers */
	@supports (backdrop-filter: blur(24px)) or (-webkit-backdrop-filter: blur(24px)) {
		.header-container {
			/* Significantly reduced background opacity for more transparency */
			background: hsl(0deg 0% 100% / 0.25);
		}

		:global(.dark) .header-container {
			background: hsl(220deg 10% 10% / 0.25);
		}

		.backdrop {
			position: absolute;
			inset: 0;
			/* Increased blur amount */
			-webkit-backdrop-filter: blur(24px);
			backdrop-filter: blur(24px);
			/* Reduced gradient opacity */
			background: linear-gradient(to bottom, hsl(0deg 0% 95% / 0.5), transparent 50%);
			pointer-events: none;
			z-index: -1;
		}

		:global(.dark) .backdrop {
			background: linear-gradient(to bottom, hsl(220deg 10% 10% / 0.5), transparent 50%);
		}

		.backdrop-edge {
			position: absolute;
			left: 0;
			right: 0;
			bottom: 0;
			height: var(--thickness);
			background: hsl(0deg 0% 100% / 0.1);
			/* Increased blur amount */
			-webkit-backdrop-filter: blur(18px) brightness(0.97);
			backdrop-filter: blur(18px) brightness(0.97);
			transform: translateY(100%);
			pointer-events: none;
			z-index: -1;
		}

		:global(.dark) .backdrop-edge {
			background: hsl(220deg 10% 10% / 0.1);
			-webkit-backdrop-filter: blur(18px) brightness(1.03);
			backdrop-filter: blur(18px) brightness(1.03);
		}
	}

	/* Support for mask-image browsers */
	@supports (mask-image: none) or (-webkit-mask-image: none) {
		.backdrop {
			height: 200%;
			-webkit-mask-image: linear-gradient(to bottom, black 0% 50%, transparent 50% 100%);
			mask-image: linear-gradient(to bottom, black 0% 50%, transparent 50% 100%);
		}

		.backdrop-edge {
			height: 100%;
			inset: 0;
			-webkit-mask-image: linear-gradient(
				to bottom,
				black 0,
				black var(--thickness),
				transparent var(--thickness)
			);
			mask-image: linear-gradient(
				to bottom,
				black 0,
				black var(--thickness),
				transparent var(--thickness)
			);
		}
	}
</style>
