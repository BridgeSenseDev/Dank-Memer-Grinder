<script lang="ts">
	import * as Tabs from "$lib/components/ui/tabs/index.js";
	import { fade } from "svelte/transition";
	import AutoBuy from "./auto-buy.svelte";
	import AutoUse from "./auto-use.svelte";
	import General from "./general.svelte";

	let settingsCurrentTab =
		typeof window !== "undefined"
			? sessionStorage.getItem("settingsCurrentTab") || "general"
			: "general";

	$: {
		if (typeof window !== "undefined") {
			sessionStorage.setItem("settingsCurrentTab", settingsCurrentTab);
		}
	}
</script>

<div
	in:fade={{ delay: 100, duration: 250 }}
	out:fade={{ duration: 100 }}
	class="z-10 h-full space-y-4"
>
	<Tabs.Root bind:value={settingsCurrentTab} class="w-full">
		<Tabs.List class="grid w-full grid-cols-3	">
			<Tabs.Trigger value="general">General</Tabs.Trigger>
			<Tabs.Trigger value="autoBuy">Auto Buy</Tabs.Trigger>
			<Tabs.Trigger value="autoUse">Auto Use</Tabs.Trigger>
		</Tabs.List>
		<Tabs.Content value="general">
			<General />
		</Tabs.Content>
		<Tabs.Content value="autoBuy">
			<AutoBuy />
		</Tabs.Content>
		<Tabs.Content value="autoUse">
			<AutoUse />
		</Tabs.Content>
	</Tabs.Root>
</div>
