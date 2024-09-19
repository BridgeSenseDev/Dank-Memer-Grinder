<script lang="ts">
	import { Button } from "$lib/components/ui/button";
	import LogsIcon from "svelte-radix/ActivityLog.svelte";
	import SettingsIcon from "svelte-radix/Gear.svelte";
	import CommandsIcon from "svelte-radix/Slash.svelte";
	import AccountsIcon from "svelte-radix/Person.svelte";
	import { DiscordLogo, GithubLogo, Globe } from "svelte-radix";
	import { page } from "$app/stores";
	import { BrowserOpenURL } from "$lib/wailsjs/runtime/runtime";
	import { cfg } from "$lib/store";

	const routes = [
		{ path: "/", label: "Logs", icon: LogsIcon },
		{ path: "/settings", label: "Settings", icon: SettingsIcon },
		{ path: "/accounts", label: "Accounts", icon: AccountsIcon },
		{ path: "/commands", label: "Commands", icon: CommandsIcon }
	];

	$: selectedRoute = $page.url.pathname.split("/")[1];

	function toggleState() {
		cfg.update((currentConfig) => {
			return {
				...currentConfig,
				state: !currentConfig.state,
				convertValues: currentConfig.convertValues
			};
		});
	}
</script>

<div class="fixed z-20 flex h-lvh w-48 flex-col border-r-2 border-border bg-background pb-14">
	<div class="flex h-full flex-col justify-between">
		<div class="group flex flex-col gap-4 py-2">
			<nav class="grid gap-1 px-2">
				{#each routes as route}
					<a href={route.path} class="flex flex-col">
						<Button
							size="sm"
							class={`justify-start bg-transparent text-black hover:bg-primary/20 dark:text-white ${"/" + selectedRoute === route.path ? "bg-primary/20" : ""}`}
						>
							<svelte:component this={route.icon} class="mr-2 size-4" aria-hidden="true" />
							{route.label}
						</Button>
					</a>
				{/each}
			</nav>
		</div>
		<div class="flex flex-col px-2">
			<Button on:click={toggleState} variant={$cfg.state ? "default" : "destructive"}>
				{$cfg.state ? "Enabled" : "Disabled"}
			</Button>
			<div class="mt-auto flex flex-row items-center justify-evenly gap-2 p-2">
				<button on:click={() => BrowserOpenURL("https://discord.com/invite/KTrmQnhCHb")}>
					<DiscordLogo class="h-6 w-6 hover:text-primary/50" />
				</button>
				<button on:click={() => BrowserOpenURL("https://www.dankmemer.tools/")}>
					<Globe class="h-6 w-6 hover:text-primary/50" />
				</button>
				<button
					on:click={() => BrowserOpenURL("https://github.com/BridgeSenseDev/Dank-Memer-Grinder")}
				>
					<GithubLogo class="h-6 w-6 hover:text-primary/50" />
				</button>
			</div>
			<h3 class="p-1 text-center">v2.0.0-alpha13</h3>
		</div>
	</div>
</div>
