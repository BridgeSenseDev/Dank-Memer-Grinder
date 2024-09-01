<script lang="ts">
	import { cfg } from "$lib/store";
	import * as Card from "$lib/components/ui/card/index.js";
	import * as Select from "$lib/components/ui/select";
	import { Input } from "$lib/components/ui/input/index.js";
	import { Label } from "$lib/components/ui/label/index.js";
	import { Switch } from "$lib/components/ui/switch";
	import { UpdateDiscordStatus } from "$lib/wailsjs/go/main/App";

	function statusLabel(input: string): string {
		if (!input) {
			return "";
		} else if (input == "dnd") {
			return "Do Not Disturb";
		} else {
			return input.charAt(0).toUpperCase() + input.slice(1);
		}
	}

	let discordStatus = { value: $cfg.discordStatus, label: statusLabel($cfg.discordStatus) };
	let previousDiscordStatus = discordStatus.value;

	$: {
		if (discordStatus.value !== previousDiscordStatus) {
			UpdateDiscordStatus(discordStatus.value);
			$cfg.discordStatus = discordStatus.value;
			previousDiscordStatus = discordStatus.value;
		}
	}
</script>

<div class="flex flex-col space-y-2">
	<Card.Root>
		<div class="flex flex-row">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>API</Card.Title>
				<Card.Description>Required for automatic captcha solver.</Card.Description>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				<div class="flex w-full flex-row items-center space-x-2">
					<Label class="whitespace-nowrap" for="apiKey">DMG API Key</Label>
					<Input type="text" id="apiKey" bind:value={$cfg.apiKey} />
				</div>
			</Card.Content>
		</div>
	</Card.Root>
	<Card.Root>
		<div class="flex flex-row">
			<Card.Header class="w-2/6 pr-0">
				<Card.Title>Others</Card.Title>
				<Card.Description>General settings for Discord or Dank Memer.</Card.Description>
			</Card.Header>
			<Card.Content class="flex w-4/6 flex-col justify-center space-y-3 pb-0">
				<div class="flex w-full flex-row items-center space-x-2">
					<Switch id="readAlerts" bind:checked={$cfg.readAlerts} />
					<Label class="whitespace-nowrap" for="readAlerts">Auto read alerts</Label>
				</div>
				<div class="flex w-full flex-row items-center space-x-2">
					<Label class="whitespace-nowrap">Discord status</Label>
					<Select.Root bind:selected={discordStatus}>
						<Select.Trigger class="w-[180px]">
							<Select.Value placeholder="Choose discord status" />
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
