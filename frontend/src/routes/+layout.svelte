<script lang="ts">
	import '../app.postcss';
	import Nav from '$lib/components/Nav.svelte';
	import Header from '$lib/components/Header.svelte';

	import { onMount } from 'svelte';
	import { cfg, instances, layoutEventListenersSet } from '$lib/store';
	import { GetConfig, GetInstances } from '$lib/wailsjs/go/main/App';
	import { EventsOn } from '$lib/wailsjs/runtime/runtime';
	import { config, main } from '$lib/wailsjs/go/models';

	onMount(async () => {
		if (!$layoutEventListenersSet) {
			cfg.set(await GetConfig());
			instances.set(await GetInstances());

			EventsOn('configUpdate', (newCfg: config.Config) => {
				cfg.set(newCfg);
			});

			EventsOn('instancesUpdate', (newInstances: main.InstanceView[]) => {
				instances.set(newInstances);
			});

			layoutEventListenersSet.set(true);
		}
	});
</script>

<main class="grainy flex min-h-screen flex-col antialiased">
	<Header />
	<div class="flex-grow">
		<div class="flex flex-row">
			<div class="sticky">
				<Nav />
			</div>
			<div class="min-h-navbar relative left-48 mr-48 flex h-full w-full">
				<div class="flex-1 p-4">
					<slot />
				</div>
			</div>
		</div>
	</div>
</main>
