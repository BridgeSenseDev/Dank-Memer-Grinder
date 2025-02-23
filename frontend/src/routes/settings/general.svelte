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
		const [minHours, maxHours] = breakDuration;
		const [minDelay, maxDelay] = breakCooldown;
		const [minMinutes, maxMinutes] = accountStartDelay;
		const [minSeconds, maxSeconds] = buttonClickDelay;
		const [minSeconds2, maxSeconds2] = commandInterval;

		if (
			cfg.c.cooldowns.breakCooldown.minHours !== minDelay ||
			cfg.c.cooldowns.breakCooldown.maxHours !== maxDelay
		) {
			cfg.c.cooldowns.breakCooldown.minHours = minDelay;
			cfg.c.cooldowns.breakCooldown.maxHours = maxDelay;
		}

		if (
			cfg.c.cooldowns.breakDuration.minHours !== minHours ||
			cfg.c.cooldowns.breakDuration.maxHours !== maxHours
		) {
			cfg.c.cooldowns.breakDuration.minHours = minHours;
			cfg.c.cooldowns.breakDuration.maxHours = maxHours;
		}

		if (
			cfg.c.cooldowns.startDelay.minMinutes !== minMinutes ||
			cfg.c.cooldowns.startDelay.maxMinutes !== maxMinutes
		) {
			cfg.c.cooldowns.startDelay.minMinutes = minMinutes;
			cfg.c.cooldowns.startDelay.maxMinutes = maxMinutes;
		}

		if (
			cfg.c.cooldowns.buttonClickDelay.minSeconds !== minSeconds ||
			cfg.c.cooldowns.buttonClickDelay.maxSeconds !== maxSeconds
		) {
			cfg.c.cooldowns.buttonClickDelay.minSeconds = minSeconds;
			cfg.c.cooldowns.buttonClickDelay.maxSeconds = maxSeconds;
		}

		if (
			cfg.c.cooldowns.commandInterval.minSeconds !== minSeconds2 ||
			cfg.c.cooldowns.commandInterval.maxSeconds !== maxSeconds2
		) {
			cfg.c.cooldowns.commandInterval.minSeconds = minSeconds2;
			cfg.c.cooldowns.commandInterval.maxSeconds = maxSeconds2;
		}
	});

	let breakCooldown = $state([
		cfg.c.cooldowns.breakCooldown.minHours,
		cfg.c.cooldowns.breakCooldown.maxHours
	]);

	let breakDuration = $state([
		cfg.c.cooldowns.breakDuration.minHours,
		cfg.c.cooldowns.breakDuration.maxHours
	]);

	let commandInterval = $state([
		cfg.c.cooldowns.commandInterval.minSeconds,
		cfg.c.cooldowns.commandInterval.maxSeconds
	]);

	let buttonClickDelay = $state([
		cfg.c.cooldowns.buttonClickDelay.minSeconds,
		cfg.c.cooldowns.buttonClickDelay.maxSeconds
	]);

	let accountStartDelay = $state([
		cfg.c.cooldowns.startDelay.minMinutes,
		cfg.c.cooldowns.startDelay.maxMinutes
	]);

	let eventDelay = $state([
		cfg.c.cooldowns.eventDelay.minSeconds,
		cfg.c.cooldowns.eventDelay.maxSeconds
	]);
</script>

<div class="flex flex-col space-y-2">
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
				<Card.Title>Breaks</Card.Title>
				<Card.Description
					>Customizable breaks to look human and avoid detection.<br /><br />Turn off by setting
					break duration to 0.</Card.Description
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
						>Break Duration<br />{breakDuration[0].toFixed(1)} - {breakDuration[1].toFixed(1)} hours</Label
					>
					<Slider type="multiple" bind:value={breakDuration} max={20} min={0} step={0.1} />
				</div>
			</Card.Content>
		</div>
	</Card.Root>
	<Card.Root>
		<div class="flex flex-row pb-6">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Delays</Card.Title>
				<Card.Description
					>Account start delay is the time before each account starts, useful to avoiding detections
					with many accounts.<br /><br />Button click delay is the delay applied to all message
					interactions.<br /><br />Command interval is the time between each command being sent.</Card.Description
				>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				<div class="flex w-full flex-row items-center space-x-4">
					<Label class="text-sm/5 whitespace-nowrap"
						>Account Start Delay<br />{accountStartDelay[0].toFixed(1)} - {accountStartDelay[1].toFixed(
							1
						)}
						minutes</Label
					>
					<Slider type="multiple" bind:value={accountStartDelay} max={30} min={0.5} step={0.1} />
				</div>
				<div class="flex w-full flex-row items-center space-x-4">
					<Label class="text-sm/5 whitespace-nowrap"
						>Button Click Delay<br />{buttonClickDelay[0].toFixed(1)} - {buttonClickDelay[1].toFixed(
							1
						)}
						seconds</Label
					>
					<Slider type="multiple" bind:value={buttonClickDelay} max={1} min={0} step={0.1} />
				</div>
				<div class="flex w-full flex-row items-center space-x-4">
					<Label class="text-sm/5 whitespace-nowrap"
						>Command Interval<br />{commandInterval[0].toFixed(1)} - {commandInterval[1].toFixed(1)}
						seconds</Label
					>
					<Slider type="multiple" bind:value={commandInterval} max={10} min={0} step={0.1} />
				</div>
			</Card.Content>
		</div>
	</Card.Root>
	<Card.Root>
		<div class="flex flex-row pb-6">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Events</Card.Title>
				<Card.Description
					>Customize auto events to act more human like or to beat others.<br /><br />Disable auto
					events by setting events correct chance to 0.<br /><br />Events correct chance applies to
					Trivia Night, Items Guesser and Fish Guesser.</Card.Description
				>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				<div class="flex w-full flex-row items-center space-x-4">
					<Label class="text-sm/5 whitespace-nowrap"
						>Event Delay<br />{eventDelay[0].toFixed(1)} - {eventDelay[1].toFixed(1)} seconds</Label
					>
					<Slider type="multiple" bind:value={eventDelay} max={10} min={0} step={0.1} />
				</div>
				<div class="flex w-full flex-row items-center space-x-4">
					<Label class="text-sm/5 whitespace-nowrap"
						>Events Correct Chance<br />{cfg.c.eventsCorrectChance.toFixed(2)}%</Label
					>
					<Slider
						type="single"
						bind:value={cfg.c.eventsCorrectChance}
						max={1}
						min={0}
						step={0.01}
					/>
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
