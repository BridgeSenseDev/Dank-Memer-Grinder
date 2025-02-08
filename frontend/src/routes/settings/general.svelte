<script lang="ts">
	import { cfg } from "$lib/state.svelte";
	import * as Card from "$lib/components/ui/card/index.js";
	import * as Select from "$lib/components/ui/select";
	import { Slider } from "$lib/components/ui/slider/index.js";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Label } from "$lib/components/ui/label/index.js";
	import { Switch } from "$lib/components/ui/switch";
	import { UpdateDiscordStatus } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";

	let discordStatus = $state({
		value: cfg.c.discordStatus
	});

	const statusLabel = $derived(() => {
		if (!discordStatus.value) {
			return "";
		} else if (discordStatus.value === "dnd") {
			return "Do Not Disturb";
		} else {
			return discordStatus.value.charAt(0).toUpperCase() + discordStatus.value.slice(1);
		}
	});

	$effect(() => {
		const newStatus = discordStatus.value;
		const oldStatus = cfg.c.discordStatus;

		if (newStatus !== oldStatus) {
			UpdateDiscordStatus(newStatus);
			cfg.c.discordStatus = newStatus;
		}
	});

	$effect(() => {
		const [minHours, maxHours] = breakTime;
		const [minDelay, maxDelay] = breakCooldown;

		if (
			cfg.c.cooldowns.breakCooldown.minHours !== minDelay ||
			cfg.c.cooldowns.breakCooldown.maxHours !== maxDelay
		) {
			cfg.c.cooldowns.breakCooldown.minHours = minDelay;
			cfg.c.cooldowns.breakCooldown.maxHours = maxDelay;
		}

		if (
			cfg.c.cooldowns.breakTime.minHours !== minHours ||
			cfg.c.cooldowns.breakTime.maxHours !== maxHours
		) {
			cfg.c.cooldowns.breakTime.minHours = minHours;
			cfg.c.cooldowns.breakTime.maxHours = maxHours;
		}
	});

	let breakCooldown = $state([
		cfg.c.cooldowns.breakCooldown.minHours,
		cfg.c.cooldowns.breakCooldown.maxHours
	]);

	let breakTime = $state([cfg.c.cooldowns.breakTime.minHours, cfg.c.cooldowns.breakTime.maxHours]);
</script>

<div class="flex flex-col space-y-2">
	<Card.Root>
		<div class="flex flex-row pb-6">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Breaks</Card.Title>
				<Card.Description
					>Customizable breaks to look human and avoid detection.<br />Turn off by setting break
					duration to 0.</Card.Description
				>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				<div class="flex w-full flex-row items-center space-x-4">
					<Label class="text-sm/5 whitespace-nowrap"
						>Grind Duration<br />{breakCooldown[0].toFixed(1)} - {breakCooldown[1].toFixed(1)} hours</Label
					>
					<Slider type="multiple" bind:value={breakCooldown} max={5} min={0.2} step={0.1} />
				</div>
				<div class="flex w-full flex-row items-center space-x-4">
					<Label class="text-sm/5 whitespace-nowrap"
						>Break Duration<br />{breakTime[0].toFixed(1)} - {breakTime[1].toFixed(1)} hours</Label
					>
					<Slider type="multiple" bind:value={breakTime} max={20} min={0} step={0.1} />
				</div>
			</Card.Content>
		</div>
	</Card.Root>
	<Card.Root>
		<div class="flex flex-row pb-6">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>API</Card.Title>
				<Card.Description>Required for automatic captcha solver.</Card.Description>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				<div class="flex w-full flex-row items-center space-x-2">
					<Label class="whitespace-nowrap" for="apiKey">DMG API Key</Label>
					<Input type="text" id="apiKey" bind:value={cfg.c.apiKey} />
				</div>
			</Card.Content>
		</div>
	</Card.Root>
	<Card.Root>
		<div class="flex flex-row pb-6">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Others</Card.Title>
				<Card.Description>General settings for Discord or Dank Memer.</Card.Description>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				<div class="flex w-full flex-row items-center space-x-2">
					<Switch id="readAlerts" bind:checked={cfg.c.readAlerts} />
					<Label class="whitespace-nowrap" for="readAlerts">Auto read alerts</Label>
				</div>
				<div class="flex w-full flex-row items-center space-x-2">
					<Label class="whitespace-nowrap">Discord status</Label>
					<Select.Root type="single" bind:value={discordStatus.value}>
						<Select.Trigger class="w-[180px]">
							{statusLabel() ? statusLabel() : "Choose discord status"}
						</Select.Trigger>
						<Select.Content>
							<Select.Item value="online">Online</Select.Item>
							<Select.Item value="idle">Idle</Select.Item>
							<Select.Item value="dnd">Do Not Disturb</Select.Item>
							<Select.Item value="invisible">Invisible</Select.Item>
						</Select.Content>
					</Select.Root>
				</div>
			</Card.Content>
		</div>
	</Card.Root>
</div>
