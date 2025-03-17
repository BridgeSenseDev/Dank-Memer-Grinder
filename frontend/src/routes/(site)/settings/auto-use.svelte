<script lang="ts">
	import { cfg } from "$lib/state.svelte.js";
	import * as Card from "$lib/components/ui/card";
	import { Switch } from "$lib/components/ui/switch";
	import { Label } from "$lib/components/ui/label";
	import { TypedObject } from "$lib/utils.js";

	function formatString(input: string): string {
		return input
			.replace(/[0-9]{2,}/g, (match) => ` ${match} `)
			.replace(/[^A-Z0-9][A-Z]/g, (match) => `${match[0]} ${match[1]}`)
			.replace(/[A-Z][A-Z][^A-Z0-9]/g, (match) => `${match[0]} ${match[1]}${match[2]}`)
			.replace(/ {2,}/g, () => " ")
			.replace(/\s./g, (match) => match.toUpperCase())
			.replace(/^./, (match) => match.toUpperCase())
			.trim();
	}

	type AutoUseType = Record<
		string,
		{
			state: boolean;
		}
	>;

	const autoUse = cfg.c.autoUse as unknown as AutoUseType;
</script>

<div class="flex flex-col space-y-2">
	<Card.Root>
		<div class="flex flex-row pb-6">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Auto Reuse</Card.Title>
				<Card.Description
					>Items will be used again through Dank's DM's after expiry.
				</Card.Description>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				{#each TypedObject.keys(autoUse) as autoUseKey (autoUseKey)}
					<div class="flex w-1/2 flex-row items-center space-x-2">
						<Switch id={autoUseKey} bind:checked={autoUse[autoUseKey].state} />
						<Label for={autoUseKey}>{formatString(autoUseKey)}</Label>
					</div>
				{/each}
			</Card.Content>
		</div>
	</Card.Root>
</div>
