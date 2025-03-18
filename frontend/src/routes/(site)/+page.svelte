<script lang="ts">
	import * as Tabs from "$lib/components/ui/tabs";
	import { fade } from "svelte/transition";
	import { type LogEntry, logs } from "$lib/state.svelte.js";
	import { onMount } from "svelte";
	import LogItem from "$lib/components/LogItem.svelte";

	let mainCurrentTab = $state("important");
	let containerHeight = $state("auto");
	let containerRef: HTMLDivElement | null = null;

	let visibleStartIndex = $state(0);
	let visibleItemCount = $state(100);

	mainCurrentTab = sessionStorage.getItem("mainCurrentTab") || "important";

	$effect(() => {
		sessionStorage.setItem("mainCurrentTab", mainCurrentTab);
	});

	$effect(() => {
		scrollToBottom();
	});

	function scrollToBottom() {
		setTimeout(() => {
			const currentContainer = document.querySelector(".log-container");
			if (currentContainer) {
				currentContainer.scrollTop = currentContainer.scrollHeight;
			}
		}, 0);
	}

	function handleScroll(e: Event, logEntries: LogEntry[]) {
		const container = e.target as HTMLDivElement;
		const scrollTop = container.scrollTop;
		const itemHeight = 24;

		visibleStartIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - 10);
		visibleItemCount = Math.ceil(container.clientHeight / itemHeight) + 20;

		if (visibleStartIndex + visibleItemCount > logEntries.length) {
			visibleStartIndex = Math.max(0, logEntries.length - visibleItemCount);
		}
	}

	onMount(() => {
		const calculateHeight = () => {
			if (containerRef) {
				const rect = containerRef.getBoundingClientRect();
				const viewportHeight = window.innerHeight;
				const availableHeight = viewportHeight - rect.top - 20;
				containerHeight = `${availableHeight}px`;
			}
		};

		calculateHeight();
		window.addEventListener("resize", calculateHeight);
		scrollToBottom();

		return () => {
			window.removeEventListener("resize", calculateHeight);
		};
	});
</script>

<div
	bind:this={containerRef}
	in:fade={{ delay: 100, duration: 250 }}
	out:fade={{ duration: 100 }}
	class="z-10 flex flex-col"
	style="height: {containerHeight}; max-height: {containerHeight};"
>
	<Tabs.Root bind:value={mainCurrentTab} class="flex h-full w-full flex-col">
		<div class="bg-background/95 sticky top-0 z-10 backdrop-blur-sm">
			<Tabs.List class="grid w-full grid-cols-3">
				<Tabs.Trigger value="important">Important</Tabs.Trigger>
				<Tabs.Trigger value="others">Others</Tabs.Trigger>
				<Tabs.Trigger value="discord">Discord</Tabs.Trigger>
			</Tabs.List>
		</div>

		<div class="flex-1 overflow-hidden">
			{#each ["important", "others", "discord"] as tabName}
				<Tabs.Content value={tabName} class="h-full">
					<div
						class="log-container border-ring h-full w-full overflow-auto rounded-md border-2 bg-transparent px-3 py-2 text-sm shadow-xs outline-hidden"
						style="max-height: calc({containerHeight} - 45px);"
						onscroll={(e) => handleScroll(e, logs[`${tabName}Logs`])}
					>
						{#if logs[`${tabName}Logs`].length === 0}
							<div class="text-gray-400 italic">No logs yet</div>
						{:else}
							<div style="height: {visibleStartIndex * 24}px"></div>

							{#each logs[`${tabName}Logs`].slice(visibleStartIndex, visibleStartIndex + visibleItemCount) as log (log.id)}
								<LogItem
									timestamp={log.timestamp}
									type={log.type}
									username={log.username}
									message={log.message}
								/>
							{/each}
						{/if}
					</div>
				</Tabs.Content>
			{/each}
		</div>
	</Tabs.Root>
</div>

<style>
	:global(.h-full > [role="tabpanel"]) {
		height: 100%;
	}

	.log-container {
		scroll-behavior: smooth;
	}
</style>
