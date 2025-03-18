<script lang="ts">
	import * as Tabs from "$lib/components/ui/tabs";
	import { fade } from "svelte/transition";
	import { logs } from "$lib/state.svelte.js";
	import { onMount } from "svelte";
	import LogItem from "$lib/components/LogItem.svelte";
	import type { LogEntry } from "$lib/state.svelte";

	interface TabScrollState {
		visibleStartIndex: number;
		visibleItemCount: number;
		scrollTop: number;
	}

	function getLogsForTab(tabName: string): LogEntry[] {
		switch (tabName) {
			case "important":
				return logs.importantLogs;
			case "others":
				return logs.othersLogs;
			case "discord":
				return logs.discordLogs;
			default:
				return [];
		}
	}

	let mainCurrentTab = $state("important");
	let containerHeight = $state("auto");
	let containerRef: HTMLDivElement | null = null;

	let tabScrollStates: Record<string, TabScrollState> = $state({
		important: { visibleStartIndex: 0, visibleItemCount: 100, scrollTop: 0 },
		others: { visibleStartIndex: 0, visibleItemCount: 100, scrollTop: 0 },
		discord: { visibleStartIndex: 0, visibleItemCount: 100, scrollTop: 0 }
	});

	const ITEM_HEIGHT = 24;
	const BUFFER_ITEMS = 50;

	mainCurrentTab = sessionStorage.getItem("mainCurrentTab") || "important";

	$effect(() => {
		sessionStorage.setItem("mainCurrentTab", mainCurrentTab);
	});

	$effect(() => {
		scrollToBottom(mainCurrentTab);
	});

	function scrollToBottom(tabName: string) {
		setTimeout(() => {
			const currentContainer = document.querySelector(`.log-container-${tabName}`);
			if (currentContainer) {
				currentContainer.scrollTop = currentContainer.scrollHeight;
				updateTabScrollState(tabName, currentContainer);
			}
		}, 0);
	}

	function updateTabScrollState(tabName: string, container: Element) {
		const scrollTop = container.scrollTop;
		tabScrollStates[tabName].scrollTop = scrollTop;

		const visibleStartIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER_ITEMS);
		const visibleItemCount = Math.ceil(container.clientHeight / ITEM_HEIGHT) + BUFFER_ITEMS * 2;

		tabScrollStates[tabName].visibleStartIndex = visibleStartIndex;
		tabScrollStates[tabName].visibleItemCount = visibleItemCount;
	}

	function handleScroll(e: Event, tabName: string) {
		const container = e.target as HTMLDivElement;
		updateTabScrollState(tabName, container);
	}

	function handleTabChange(tabName: string) {
		setTimeout(() => {
			const container = document.querySelector(`.log-container-${tabName}`);
			if (container) {
				container.scrollTop = tabScrollStates[tabName].scrollTop;
			}
		}, 0);
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
		scrollToBottom(mainCurrentTab);

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
	<Tabs.Root
		bind:value={mainCurrentTab}
		class="flex h-full w-full flex-col"
		onValueChange={(value) => handleTabChange(value)}
	>
		<div class="bg-background/95 sticky top-0 z-10 backdrop-blur-sm">
			<Tabs.List class="grid w-full grid-cols-3">
				<Tabs.Trigger value="important">Important</Tabs.Trigger>
				<Tabs.Trigger value="others">Others</Tabs.Trigger>
				<Tabs.Trigger value="discord">Discord</Tabs.Trigger>
			</Tabs.List>
		</div>

		<div class="flex-1 overflow-hidden">
			{#each ["important", "others", "discord"] as tabName (tabName)}
				<Tabs.Content value={tabName} class="h-full">
					<div
						class="log-container-{tabName} border-ring scrollbar-thin scrollbar-track-transparent scrollbar-thumb-primary/50 relative h-full w-full overflow-y-auto scroll-auto rounded-md border-2 bg-transparent px-3 py-2 text-sm shadow-xs outline-hidden"
						style="max-height: calc({containerHeight} - 45px);"
						onscroll={(e) => handleScroll(e, tabName)}
					>
						{#if getLogsForTab(tabName).length === 0}
							<div class="text-gray-400 italic">No logs yet</div>
						{:else}
							<div
								class="spacer-top pointer-events-none select-none"
								style="height: {tabScrollStates[tabName].visibleStartIndex * ITEM_HEIGHT}px;"
							></div>

							{#each getLogsForTab(tabName).slice(tabScrollStates[tabName].visibleStartIndex, tabScrollStates[tabName].visibleStartIndex + tabScrollStates[tabName].visibleItemCount) as log (log.id)}
								<LogItem
									timestamp={log.timestamp}
									type={log.type}
									username={log.username}
									message={log.message}
								/>
							{/each}

							<div
								class="spacer-bottom pointer-events-none select-none"
								style="height: {Math.max(
									0,
									getLogsForTab(tabName).length -
										(tabScrollStates[tabName].visibleStartIndex +
											tabScrollStates[tabName].visibleItemCount)
								) * ITEM_HEIGHT}px;"
							></div>
						{/if}
					</div>
				</Tabs.Content>
			{/each}
		</div>
	</Tabs.Root>
</div>
