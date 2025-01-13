<script lang="ts">
	import * as Tabs from "$lib/components/ui/tabs/index.js";
	import { fade } from "svelte/transition";
	import { logs } from "$lib/state.svelte";

	let mainCurrentTab = $state("important");

	mainCurrentTab = sessionStorage.getItem("mainCurrentTab") || "important";

	$effect(() => {
		sessionStorage.setItem("mainCurrentTab", mainCurrentTab);
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
				class="border-input ring-ring flex h-full min-h-[60px] w-full rounded-md border bg-transparent px-3 py-2 text-sm ring-1 shadow-xs outline-hidden"
				bind:innerHTML={logs.importantLogs}
				contenteditable="false"
			></div>
		</Tabs.Content>
		<Tabs.Content value="others" class="h-full">
			<div
				class="border-input ring-ring flex h-full min-h-[60px] w-full rounded-md border bg-transparent px-3 py-2 text-sm ring-1 shadow-xs outline-hidden"
				bind:innerHTML={logs.othersLogs}
				contenteditable="false"
			></div>
		</Tabs.Content>
		<Tabs.Content value="discord" class="h-full">
			<div
				class="border-input ring-ring flex h-full min-h-[60px] w-full rounded-md border bg-transparent px-3 py-2 text-sm ring-1 shadow-xs outline-hidden"
				bind:innerHTML={logs.discordLogs}
				contenteditable="false"
			></div>
		</Tabs.Content>
	</Tabs.Root>
</div>
