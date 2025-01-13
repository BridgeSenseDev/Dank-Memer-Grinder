<script lang="ts">
	import { Button } from "$lib/components/ui/button";
	import LogsIcon from "svelte-radix/ActivityLog.svelte";
	import SettingsIcon from "svelte-radix/Gear.svelte";
	import CommandsIcon from "svelte-radix/Slash.svelte";
	import AccountsIcon from "svelte-radix/Person.svelte";
	import { DiscordLogo, GithubLogo, Globe } from "svelte-radix";
	import { page } from "$app/state";
	import { Browser } from "@wailsio/runtime";
	import { cfg } from "$lib/state.svelte";

	const routes = [
		{ path: "/", label: "Logs", icon: LogsIcon },
		{ path: "/settings", label: "Settings", icon: SettingsIcon },
		{ path: "/accounts", label: "Accounts", icon: AccountsIcon },
		{ path: "/commands", label: "Commands", icon: CommandsIcon }
	];

	let selectedRoute = $derived(page.url.pathname.split("/")[1]);

	function toggleState() {
		cfg.c.state = !cfg.c.state;
	}
</script>

<div class="border-border bg-background fixed z-20 flex h-lvh w-48 flex-col border-r-2 pb-14">
	<div class="flex h-full flex-col justify-between">
		<div class="group flex flex-col gap-4 py-2">
			<nav class="grid gap-1 px-2">
				{#each routes as route}
					<a href={route.path} class="flex flex-col">
						<Button
							size="sm"
							class={`hover:bg-primary/20 justify-start bg-transparent text-black dark:text-white ${"/" + selectedRoute === route.path ? "bg-primary/20" : ""}`}
						>
							<route.icon class="mr-2 size-4" aria-hidden="true" />
							{route.label}
						</Button>
					</a>
				{/each}
			</nav>
		</div>
		<div class="flex flex-col px-2">
			<Button onclick={toggleState} variant={cfg.c.state ? "default" : "destructive"}>
				{cfg.c.state ? "Enabled" : "Disabled"}
			</Button>
			<div class="mt-auto flex flex-row items-center justify-evenly gap-2 p-2">
				<button
					class="cursor-pointer"
					onclick={() => Browser.OpenURL("https://discord.com/invite/KTrmQnhCHb")}
				>
					<DiscordLogo class="hover:text-primary/50 h-6 w-6" />
				</button>
				<button
					class="cursor-pointer"
					onclick={() => Browser.OpenURL("https://www.dankmemer.tools/")}
				>
					<Globe class="hover:text-primary/50 h-6 w-6" />
				</button>
				<button
					class="cursor-pointer"
					onclick={() => Browser.OpenURL("https://github.com/BridgeSenseDev/Dank-Memer-Grinder")}
				>
					<GithubLogo class="hover:text-primary/50 h-6 w-6" />
				</button>
			</div>
			<h3 class="p-1 text-center">v2.0.0-alpha13</h3>
		</div>
	</div>
</div>
