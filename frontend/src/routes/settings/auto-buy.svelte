<script lang="ts">
	import { cfg } from '$lib/store';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Switch } from '$lib/components/ui/switch';
	import { Label } from '$lib/components/ui/label/index.js';

	function formatString(input: string): string {
		return input
			.replace(/[0-9]{2,}/g, (match) => ` ${match} `)
			.replace(/[^A-Z0-9][A-Z]/g, (match) => `${match[0]} ${match[1]}`)
			.replace(/[A-Z][A-Z][^A-Z0-9]/g, (match) => `${match[0]} ${match[1]}${match[2]}`)
			.replace(/[ ]{2,}/g, (match) => ' ')
			.replace(/\s./g, (match) => match.toUpperCase())
			.replace(/^./, (match) => match.toUpperCase())
			.trim();
	}
</script>

{#if $cfg.gui}
	<Card.Root>
		<div class="flex flex-row">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Commands</Card.Title>
				<Card.Description>Automatically purchase items needed for some commands</Card.Description>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				{#each Object.keys($cfg.autoBuy) as autoBuyKey (autoBuyKey)}
					<div class="flex w-1/2 flex-row items-center space-x-2">
						<Switch id={autoBuyKey} bind:checked={$cfg.autoBuy[autoBuyKey]} />
						<Label for={autoBuyKey}>{formatString(autoBuyKey)}</Label>
					</div>
				{/each}
			</Card.Content>
		</div>
	</Card.Root>
{/if}
