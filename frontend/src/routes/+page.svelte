<script lang="ts">
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import { fade } from 'svelte/transition';
	import { EventsOn } from '$lib/wailsjs/runtime/runtime';
	import { onMount } from 'svelte';
	import { importantLogs, othersLogs, discordLogs, logsEventListenersSet } from '$lib/store';

	let mainCurrentTab =
		typeof window !== 'undefined'
			? sessionStorage.getItem('mainCurrentTab') || 'important'
			: 'important';

	{
		if (typeof window !== 'undefined') {
			sessionStorage.setItem('mainCurrentTab', mainCurrentTab);
		}
	}

	onMount(async () => {
		if (!$logsEventListenersSet) {
			const logWithTime = (logs: string, type: string, username: string, msg: string) => {
				const now = new Date();
				const hours = now.getHours();
				const minutes = now.getMinutes();
				const ampm = hours >= 12 ? 'PM' : 'AM';
				const formattedTime = `${hours % 12 || 12}:${minutes < 10 ? '0' : ''}${minutes}${ampm}`;

				logs += `<span class="text-gray-400">${formattedTime} `;

				if (type === 'INF') {
					logs += `<span class="text-green-500">INF `;
				} else if (type === 'ERR') {
					logs += `<span class="text-red-500">ERR `;
				}
				logs +=
					`<span class="text-sky-500">` + username + '<span class="text-white"> ' + msg + '<br>';

				return logs;
			};

			EventsOn('logImportant', (type: string, username: string, msg: string) => {
				importantLogs.update((logs) => logWithTime(logs, type, username, msg));
			});

			EventsOn('logOthers', (type: string, username: string, msg: string) => {
				othersLogs.update((logs) => logWithTime(logs, type, username, msg));
			});

			EventsOn('logDiscord', (type: string, username: string, msg: string) => {
				discordLogs.update((logs) => logWithTime(logs, type, username, msg));
			});

			logsEventListenersSet.set(true);
		}
	});
</script>

<div
	in:fade={{ delay: 100, duration: 250 }}
	out:fade={{ duration: 100 }}
	class="z-10 h-full space-y-4"
>
	<Tabs.Root bind:value={mainCurrentTab} class="h-full w-full pb-9">
		<Tabs.List class="grid w-full grid-cols-3">
			<Tabs.Trigger value="important">Important</Tabs.Trigger>
			<Tabs.Trigger value="others">Others</Tabs.Trigger>
			<Tabs.Trigger value="discord">Discord</Tabs.Trigger>
		</Tabs.List>
		<Tabs.Content value="important" class="h-full">
			<div
				class="border-input ring-ring flex h-full min-h-[60px] w-full rounded-md border bg-transparent px-3 py-2 text-sm shadow-sm outline-none ring-1"
				bind:innerHTML={$importantLogs}
				contenteditable="false"
			></div>
		</Tabs.Content>
		<Tabs.Content value="others" class="h-full">
			<div
				class="border-input ring-ring flex h-full min-h-[60px] w-full rounded-md border bg-transparent px-3 py-2 text-sm shadow-sm outline-none ring-1"
				bind:innerHTML={$othersLogs}
				contenteditable="false"
			></div>
		</Tabs.Content>
		<Tabs.Content value="discord" class="h-full">
			<div
				class="border-input ring-ring flex h-full min-h-[60px] w-full rounded-md border bg-transparent px-3 py-2 text-sm shadow-sm outline-none ring-1"
				bind:innerHTML={$discordLogs}
				contenteditable="false"
			></div>
		</Tabs.Content>
	</Tabs.Root>
</div>
