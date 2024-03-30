<script lang="ts">
	import { cfg } from '$lib/store';
	import { Switch } from '$lib/components/ui/switch';
	import * as Card from '$lib/components/ui/card';
	import { fade } from 'svelte/transition';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

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

	function updateCfg(commandKey: string, optionKey: string, value: any) {
		cfg.update((cfg) => {
			cfg.commands[commandKey][optionKey] = value;
			return cfg;
		});
	}
</script>

<div
	in:fade={{ delay: 100, duration: 250 }}
	out:fade={{ duration: 100 }}
	class="z-10 h-full space-y-4"
>
	{#if $cfg.gui}
		{#each Object.keys($cfg.commands) as commandKey (commandKey)}
			<Card.Root
				class={`${$cfg.commands[commandKey].state ? 'border-primary bg-primary-foreground/40' : ''}`}
			>
				<Card.Header>
					<div class="flex items-center space-x-2">
						<Card.Title tag="h1">{formatString(commandKey)}</Card.Title>
						<Switch id={commandKey} bind:checked={$cfg.commands[commandKey].state} />
						<Label for={commandKey}>Enabled</Label>
					</div>
				</Card.Header>
				<Card.Content>
					<div class="flex flex-col space-y-2">
						{#each Object.keys($cfg.commands[commandKey]) as optionKey (optionKey)}
							{#if optionKey !== 'state'}
								{#if typeof $cfg.commands[commandKey][optionKey] === 'number'}
									<div class="flex w-1/2 flex-row items-center space-x-2">
										<Label class="whitespace-nowrap" for={`${commandKey}_${optionKey}`}>
											{formatString(optionKey)}
										</Label>
										<Input
											type="number"
											id={`${commandKey}_${optionKey}`}
											value={$cfg.commands[commandKey][optionKey]}
											on:input={(e) => updateCfg(commandKey, optionKey, parseInt(e.target.value))}
										/>
									</div>
								{:else if typeof $cfg.commands[commandKey][optionKey] === 'object'}
									<div class="flex w-full flex-row items-center space-x-2">
										<Label class="whitespace-nowrap" for={`${commandKey}_${optionKey}`}>
											{formatString(optionKey)}
										</Label>
										{#if optionKey === 'order'}
											<Input
												type="text"
												id={`${commandKey}_${optionKey}`}
												value={$cfg.commands[commandKey][optionKey].join(', ')}
												on:input={(e) => {
													if (e.target.value) {
														const values = e.target.value.split(',');
														const numbers = values.map((val) =>
															val ? (isNaN(Number(val)) ? 0 : Number(val)) : ''
														);
														updateCfg(commandKey, optionKey, numbers);
													} else {
														updateCfg(commandKey, optionKey, []);
													}
												}}
											/>
										{:else}
											<Input
												value={$cfg.commands[commandKey][optionKey].join(', ')}
												id={`${commandKey}_${optionKey}`}
												on:input={(e) =>
													updateCfg(commandKey, optionKey, e.target.value.split(', '))}
											/>
										{/if}
									</div>
								{/if}
							{/if}
						{/each}
					</div>
				</Card.Content>
			</Card.Root>
		{/each}
	{:else}
		<p>Loading config...</p>
	{/if}
</div>
