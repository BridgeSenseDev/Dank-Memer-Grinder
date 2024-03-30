<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import LogsIcon from 'svelte-radix/ActivityLog.svelte';
	import SettingsIcon from 'svelte-radix/Gear.svelte';
	import CommandsIcon from 'svelte-radix/Slash.svelte';
	import AccountsIcon from 'svelte-radix/Person.svelte';
	import { DiscordLogo, GithubLogo, Globe } from 'svelte-radix';
	import { page } from '$app/stores';
	import { BrowserOpenURL } from '$lib/wailsjs/runtime/runtime';
	import { cfg } from '$lib/store';

	const routes = [
		{ path: '/', label: 'Logs', icon: LogsIcon },
		{ path: '/settings', label: 'Settings', icon: SettingsIcon },
		{ path: '/accounts', label: 'Accounts', icon: AccountsIcon },
		{ path: '/commands', label: 'Commands', icon: CommandsIcon }
	];

	$: selectedRoute = $page.url.pathname.split('/')[1];

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

<div class="flex fixed pb-14 flex-col border-r-2 border-border h-lvh w-48 bg-background z-20">
	<div class="flex flex-col justify-between h-full">
		<div class="group flex flex-col gap-4 py-2">
			<nav class="grid gap-1 px-2">
				{#each routes as route}
					<a href={route.path} class="flex flex-col">
						<Button
							size="sm"
							class={`justify-start hover:bg-primary/20 bg-transparent dark:text-white text-black ${'/' + selectedRoute === route.path ? 'bg-primary/20' : ''}`}
						>
							<svelte:component this={route.icon} class="mr-2 size-4" aria-hidden="true" />
							{route.label}
						</Button>
					</a>
				{/each}
			</nav>
		</div>
		<div class="flex px-2 flex-col">
			<Button on:click={toggleState} variant={$cfg.state ? 'default' : 'destructive'}>
				{$cfg.state ? 'Enabled' : 'Disabled'}
			</Button>
			<div class="flex flex-row items-center justify-evenly p-2 gap-2 mt-auto">
				<button on:click={() => BrowserOpenURL('https://discord.com/invite/KTrmQnhCHb')}>
					<DiscordLogo class="w-6 h-6 hover:text-primary/50" />
				</button>
				<button on:click={() => BrowserOpenURL('https://www.dankmemer.tools/')}>
					<Globe class="w-6 h-6 hover:text-primary/50" />
				</button>
				<button
					on:click={() => BrowserOpenURL('https://github.com/BridgeSenseDev/Dank-Memer-Grinder')}
				>
					<GithubLogo class="w-6 h-6 hover:text-primary/50" />
				</button>
			</div>
			<h3 class="text-center p-1">v2.0.0-alpha-pre4</h3>
		</div>
	</div>
</div>
