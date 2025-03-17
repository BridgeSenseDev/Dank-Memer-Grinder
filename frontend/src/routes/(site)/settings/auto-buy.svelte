<script lang="ts">
	import { cfg } from "$lib/state.svelte.js";
	import { Input } from "$lib/components/ui/input";
	import * as Card from "$lib/components/ui/card";
	import { Switch } from "$lib/components/ui/switch";
	import { Label } from "$lib/components/ui/label";
	import { TypedObject } from "$lib/utils";

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
</script>

<div class="flex flex-col space-y-2">
	<Card.Root>
		<div class="flex flex-row pb-6">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Commands</Card.Title>
				<Card.Description>Automatically purchase items needed for some commands</Card.Description>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				{#each TypedObject.keys(cfg.c.autoBuy) as autoBuyKey (autoBuyKey)}
					{#if autoBuyKey === "huntingRifle" || autoBuyKey === "shovel"}
						<div class="flex w-1/2 flex-row items-center space-x-2">
							<Switch id={autoBuyKey} bind:checked={cfg.c.autoBuy[autoBuyKey].state} />
							<Label for={autoBuyKey}>{formatString(autoBuyKey)}</Label>
						</div>
					{/if}
				{/each}
			</Card.Content>
		</div>
	</Card.Root>
	<Card.Root>
		<div class="flex flex-row pb-6">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Life Savers</Card.Title>
				<Card.Description>
					Automatically buy life savers when below the set amount.<br />
					Accounts will buy the maximum possible if it can't afford the set amount.
				</Card.Description>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				<div class="flex w-1/2 flex-row items-center space-x-2">
					<Switch id="lifeSavers" bind:checked={cfg.c.autoBuy.lifeSavers.state} />
					<Label for="lifeSavers">Life Savers</Label>
				</div>
				<div class="flex w-1/2 flex-row items-center space-x-2">
					<Label for="lifeSaversAmount">Amount</Label>
					<Input bind:value={cfg.c.autoBuy.lifeSavers.amount} id="lifeSaversAmount" type="number" />
				</div>
			</Card.Content>
		</div>
	</Card.Root>
</div>
