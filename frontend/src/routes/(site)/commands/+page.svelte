<script lang="ts">
	import { cfg } from "$lib/state.svelte";
	import { Switch } from "$lib/components/ui/switch";
	import * as Select from "$lib/components/ui/select/index.js";
	import * as Card from "$lib/components/ui/card";
	import { Checkbox } from "$lib/components/ui/checkbox";
	import { fade } from "svelte/transition";
	import { Input } from "$lib/components/ui/input";
	import { Label } from "$lib/components/ui/label";
	import { TypedObject } from "$lib/utils.js";
	import {
		AdventureOption,
		type CommandsConfig,
		FishLocation
	} from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/config";
	import { Slider } from "$lib/components/ui/slider";

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

	function updateCfg(
		commandKey: string,
		optionKey: string,
		value: string[] | string | number | boolean | Event
	) {
		if (value instanceof Event) {
			value = (value.target as HTMLInputElement).value;
			if (value.includes(",")) {
				value = value.split(",").map((val) => val.trim());
			}
		}

		if (Array.isArray(commands[commandKey][optionKey])) {
			if (!Array.isArray(value)) {
				value = [String(value)];
			}
		} else if (typeof commands[commandKey][optionKey] === "number") {
			value = Number(value);
		}
		commands[commandKey][optionKey] = value;
	}

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const commands = cfg.c.commands as CommandsConfig & Record<string, any>;

	const enumMap = {
		AdventureOption,
		FishLocation
	};

	function isEnum(value: string): boolean {
		return Object.keys(enumMap).includes(
			String(value).charAt(0).toUpperCase() + String(value).slice(1)
		);
	}

	function getEnumValues(enumName: string): string[] {
		const enumObject =
			enumMap[
				(String(enumName).charAt(0).toUpperCase() +
					String(enumName).slice(1)) as keyof typeof enumMap
			];

		return Object.values(enumObject).filter((v) => v !== "");
	}

	let fishOnlyEnabled = $state(false);
	let backupCommandsState: Record<string, boolean> = {};

	$effect(() => {
		if (commands.fish.state && commands.fish.fishOnly) {
			fishOnlyEnabled = true;
		}
	});

	function toggle(option: string, value: boolean | Event) {
		if (value instanceof Event) {
			value = (value.target as HTMLInputElement).checked;
		}

		if (option === "fishOnly") {
			fishOnlyEnabled = value;
			if (value) {
				for (const command in commands) {
					if (command !== "fish") {
						backupCommandsState[command] = commands[command].state;
						commands[command].state = false;
					}
				}
			} else {
				for (const command in backupCommandsState) {
					if (command !== "fish") {
						commands[command].state = backupCommandsState[command] ?? commands[command].state;
					}
				}
			}
		} else if (option === "fish") {
			if (!value && fishOnlyEnabled) {
				fishOnlyEnabled = false;
				for (const command in backupCommandsState) {
					if (command !== "fish") {
						commands[command].state = backupCommandsState[command] ?? commands[command].state;
					}
				}
			} else if (value && commands.fish.fishOnly) {
				fishOnlyEnabled = true;
				for (const command in commands) {
					if (command !== "fish") {
						backupCommandsState[command] = commands[command].state;
						commands[command].state = false;
					}
				}
			}
		}
	}

	let fishOnlyDelay = $state([
		commands["fish"].fishOnlyDelay.minSeconds,
		commands["fish"].fishOnlyDelay.maxSeconds
	]);

	$effect(() => {
		if (commands.fish.fishOnly) {
			fishOnlyDelay = [
				commands["fish"].fishOnlyDelay.minSeconds,
				commands["fish"].fishOnlyDelay.maxSeconds
			];
		}
	});
</script>

<div
	in:fade={{ delay: 100, duration: 250 }}
	out:fade={{ duration: 100 }}
	class="z-10 h-full space-y-4"
>
	{#if cfg.c.gui}
		{#each TypedObject.keys(commands) as commandKey (commandKey)}
			<Card.Root
				class={`${commands[commandKey].state ? "border-primary bg-primary-foreground/40" : ""}`}
			>
				<Card.Header>
					<div class="flex items-center space-x-2">
						<Card.Title>{formatString(commandKey)}</Card.Title>
						<Switch
							id={commandKey}
							bind:checked={commands[commandKey].state}
							disabled={fishOnlyEnabled && commandKey !== "fish"}
							onCheckedChange={(e) => toggle(commandKey, e)}
						/>
						<Label for={commandKey}>Enabled</Label>
					</div>
				</Card.Header>
				<Card.Content>
					<div class="flex flex-col space-y-2">
						{#each TypedObject.keys(commands[commandKey]) as optionKey (optionKey)}
							{#if optionKey !== "state"}
								{#if typeof commands[commandKey][optionKey] === "string" && isEnum(optionKey)}
									<div class="flex w-1/2 flex-row items-center space-x-2">
										<Label class="whitespace-nowrap" for={`${commandKey}_${optionKey}`}>
											{formatString(optionKey)}
										</Label>
										<Select.Root bind:value={commands[commandKey][optionKey]} type="single">
											<Select.Trigger class="w-[180px]"
												>{commands[commandKey][optionKey]}</Select.Trigger
											>
											<Select.Content>
												{#each getEnumValues(optionKey) as enumValue}
													<Select.Item value={enumValue}>{enumValue}</Select.Item>
												{/each}
											</Select.Content>
										</Select.Root>
									</div>
								{:else if commands[commandKey][optionKey] instanceof Array && isEnum(optionKey)}
									<div class="flex w-1/2 flex-row items-center space-x-2">
										<Label class="whitespace-nowrap" for={`${commandKey}_${optionKey}`}>
											{formatString(optionKey)}
										</Label>
										<Select.Root bind:value={commands[commandKey][optionKey]} type="multiple">
											<Select.Trigger>
												Select {formatString(optionKey)}s
											</Select.Trigger>
											<Select.Content>
												{#each getEnumValues(optionKey) as enumValue}
													<Select.Item value={enumValue}>
														{enumValue}
													</Select.Item>
												{/each}
											</Select.Content>
										</Select.Root>
									</div>
								{:else if typeof commands[commandKey][optionKey] === "string"}
									<div class="flex w-1/2 flex-row items-center space-x-2">
										<Label class="whitespace-nowrap" for={`${commandKey}_${optionKey}`}>
											{formatString(optionKey)}
										</Label>
										<Input
											type="text"
											id={`${commandKey}_${optionKey}`}
											value={commands[commandKey][optionKey]}
											oninput={(e) => updateCfg(commandKey, optionKey, e)}
										/>
									</div>
								{:else if typeof commands[commandKey][optionKey] === "number"}
									<div class="flex w-1/2 flex-row items-center space-x-2">
										<Label class="whitespace-nowrap" for={`${commandKey}_${optionKey}`}>
											{formatString(optionKey)}
										</Label>
										<Input
											type="number"
											id={`${commandKey}_${optionKey}`}
											value={commands[commandKey][optionKey]}
											oninput={(e) => updateCfg(commandKey, optionKey, e)}
										/>
									</div>
								{:else if typeof commands[commandKey][optionKey] === "boolean"}
									<div class="flex w-full flex-row items-center space-x-2">
										<Checkbox
											id={`${commandKey}_${optionKey}`}
											bind:checked={commands[commandKey][optionKey]}
											onCheckedChange={(e) => toggle(optionKey, e)}
										/>
										<Label
											class="cursor-pointer whitespace-nowrap"
											for={`${commandKey}_${optionKey}`}
										>
											{formatString(optionKey)}
										</Label>
									</div>
								{:else if commands[commandKey][optionKey] instanceof Array}
									<div class="flex w-full flex-row items-center space-x-2">
										<Label class="whitespace-nowrap" for={`${commandKey}_${optionKey}`}>
											{formatString(optionKey)}
										</Label>
										{#if optionKey === "order"}
											<Input
												type="text"
												id={`${commandKey}_${optionKey}`}
												value={commands[commandKey][optionKey].join(", ")}
												oninput={(e) => {
													updateCfg(commandKey, optionKey, e);
												}}
											/>
										{:else}
											<Input
												value={commands[commandKey][optionKey].join(", ")}
												id={`${commandKey}_${optionKey}`}
												oninput={(e) => updateCfg(commandKey, optionKey, e)}
											/>
										{/if}
									</div>
								{:else if optionKey === "fishOnlyDelay" && commands.fish.fishOnly}
									<div class="flex w-1/2 flex-row items-center space-x-2">
										<Label class="whitespace-nowrap" for={`${commandKey}_${optionKey}`}>
											{formatString(optionKey)}
											({fishOnlyDelay[0].toFixed(1)} - {fishOnlyDelay[1].toFixed(1)} seconds)
										</Label>
										<Slider
											type="multiple"
											bind:value={fishOnlyDelay}
											max={20}
											min={0}
											step={0.1}
										/>
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
