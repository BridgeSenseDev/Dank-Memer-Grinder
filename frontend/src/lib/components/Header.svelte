<script lang="ts">
	import { page } from "$app/stores";
	import { Button } from "$lib/components/ui/button";
	import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
	import { cfg } from "$lib/store";
	import * as Select from "$lib/components/ui/select";
	import { Moon, Sun } from "svelte-radix";

	let theme: string;
	let sunClass = "";
	let moonClass = "";

	$: if ($cfg.gui) {
		theme = $cfg.gui.theme;
		setTheme(theme);
	}

	function setTheme(theme: string) {
		$cfg.gui.theme = theme;

		let isDark = theme === "dark";
		if (theme === "system") {
			isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
		}
		sunClass = `h-[1.2rem] w-[1.2rem] transition-all ${isDark ? "rotate-90 scale-0" : "rotate-0 scale-100"}`;
		moonClass = `absolute h-[1.2rem] w-[1.2rem] transition-all ${isDark ? "rotate-0 scale-100" : "rotate-90 scale-0"}`;

		const handleThemeChange = (e: MediaQueryListEvent) => {
			if (theme === "system") {
				isDark = e.matches;

				sunClass = `h-[1.2rem] w-[1.2rem] transition-all ${isDark ? "rotate-90 scale-0" : "rotate-0 scale-100"}`;
				moonClass = `absolute h-[1.2rem] w-[1.2rem] transition-all ${isDark ? "rotate-0 scale-100" : "rotate-90 scale-0"}`;
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
		cfg.update((currentCfg) => {
			for (let command in currentCfg.commands) {
				(currentCfg.commands as any)[command].state = state;
			}
			return currentCfg;
		});
	}

	$: title = ($page.url.pathname.split("/")[1] || "logs")
		.split(" ")
		.map((word) => (word ? word.charAt(0).toUpperCase() + word.slice(1) : ""))
		.join(" ");
</script>

<div class="sticky top-0 z-30 flex w-full flex-row border-b border-border backdrop-blur">
	<div class="flex h-14 max-w-48 items-center border-b border-r-2 border-border px-2">
		<Select.Root preventScroll={false}>
			<Select.Trigger class="w-[180px]">
				<Select.Value placeholder="config.json" />
			</Select.Trigger>
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
					<Button on:click={() => toggleCommands(true)}>Enable all</Button>
					<Button variant="destructive" on:click={() => toggleCommands(false)}>Disable all</Button>
				{/if}
				<DropdownMenu.Root preventScroll={false}>
					<DropdownMenu.Trigger asChild let:builder>
						<Button builders={[builder]} variant="outline" size="icon">
							<Sun class={sunClass} />
							<Moon class={moonClass} />
							<span class="sr-only">Toggle theme</span>
						</Button>
					</DropdownMenu.Trigger>
					<DropdownMenu.Content align="end">
						<DropdownMenu.Item on:click={() => setTheme("light")}>Light</DropdownMenu.Item>
						<DropdownMenu.Item on:click={() => setTheme("dark")}>Dark</DropdownMenu.Item>
						<DropdownMenu.Item on:click={() => setTheme("system")}>System</DropdownMenu.Item>
					</DropdownMenu.Content>
				</DropdownMenu.Root>
			</div>
		{/if}
	</div>
</div>
