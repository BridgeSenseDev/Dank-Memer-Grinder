<script lang="ts">
	import { MagicWand, Person } from "svelte-radix";
	import { Label } from "$lib/components/ui/label";
	import { Input } from "$lib/components/ui/input";
	import * as Select from "$lib/components/ui/select";
	import * as Dialog from "$lib/components/ui/dialog";
	import { Button } from "$lib/components/ui/button/index.js";
	import * as DropdownMenu from "$lib/components/ui/dropdown-menu/index.js";
	import { cfg } from "$lib/state.svelte";
	import { Plus } from "lucide-svelte";
	import { StartInstance } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";

	let individualToken = "";
	let individualChannelID = "";
	let accountErrorMessage = "";

	async function addAccount(token: string, channelID: string): Promise<boolean> {
		const accounts = cfg.c.accounts ?? [];

		if (accounts.find((acc) => acc.token === token)) {
			accountErrorMessage = "Account with that token already exists!";
			return false;
		}

		const accountCfg = {
			token: token,
			channelID: channelID,
			state: false
		};

		cfg.c.accounts = [...accounts, accountCfg];

		try {
			await new Promise((r) => setTimeout(r, 100));
			await StartInstance(accountCfg, "ready", new Date().toISOString());
			accountErrorMessage = "";
			return true;
		} catch (err: unknown) {
			if (err instanceof Error) {
				accountErrorMessage = "Failed to add account: " + err.message;
			}
			return false;
		}
	}

	async function handleFileChange(event: Event) {
		const input = event.target as HTMLInputElement;
		const files = input.files;
		if (files) {
			const file = files[0];
			const reader = new FileReader();

			reader.onload = async (e) => {
				if (e.target !== null) {
					await parseAndAddAccounts(e.target.result as string);
				}
			};

			reader.readAsText(file);
		}
	}

	async function parseAndAddAccounts(fileContent: string) {
		const lines = fileContent.split("\n");

		for (const line of lines) {
			const trimmedLine = line.trim();

			switch (format.value) {
				case "token":
					await addAccount(trimmedLine, "");
					break;
				case '"token"': {
					const tokenMatch = trimmedLine.match(/"(.*?)"/);
					if (tokenMatch) {
						await addAccount(tokenMatch[1], "");
					}
					break;
				}
				case "token id": {
					let parts = trimmedLine.split(" ");
					if (parts.length >= 2) {
						await addAccount(parts[0], parts[1]);
					}
					break;
				}
				case "id token": {
					let parts = trimmedLine.split(" ");
					if (parts.length >= 2) {
						await addAccount(parts[1], parts[0]);
					}
					break;
				}
				case "token: id": {
					let colonParts = trimmedLine.split(":");
					if (colonParts.length >= 2) {
						await addAccount(colonParts[0].trim(), colonParts[1].trim());
					}
					break;
				}
				case "id: token": {
					let colonParts = trimmedLine.split(":");
					if (colonParts.length >= 2) {
						await addAccount(colonParts[1].trim(), colonParts[0].trim());
					}
					break;
				}
			}
		}
	}

	let openSingleAccount = false;
	let openBulkAccounts = false;
	let format = { value: "token id", label: "token id" };
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="ghost" size="icon" class="w-full rounded-t-none border">
				<span class="sr-only">Actions</span>
				<Plus class="h-5" />
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="center">
		<DropdownMenu.Group>
			<DropdownMenu.GroupHeading>Actions</DropdownMenu.GroupHeading>
			<DropdownMenu.Item onclick={() => (openSingleAccount = true)}>
				<Person class="mr-1" /> Single account
			</DropdownMenu.Item>
			<DropdownMenu.Item
				onclick={() => (openBulkAccounts = true)}
				class="text-primary hover:text-primary"
			>
				<MagicWand class="mr-1" /> Bulk accounts
			</DropdownMenu.Item>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>

<Dialog.Root bind:open={openSingleAccount}>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>Add account</Dialog.Title>
			<Dialog.Description>
				Enter the token and channel ID for your account here. Click save when you're done.
			</Dialog.Description>
		</Dialog.Header>
		<div class="grid gap-4 py-4">
			<div class="grid grid-cols-4 items-center gap-4">
				<Label for="token" class="text-right">Token</Label>
				<Input id="token" class="col-span-3" bind:value={individualToken} />
			</div>
			<div class="grid grid-cols-4 items-center gap-4">
				<Label for="channelID" class="text-right">Channel ID</Label>
				<Input type="text" id="channelID" class="col-span-3" bind:value={individualChannelID} />
			</div>
			{#if accountErrorMessage}
				<div class="text-center text-red-600">{accountErrorMessage}</div>
			{/if}
		</div>
		<Dialog.Footer>
			<Button
				type="submit"
				onclick={async () => {
					const success = await addAccount(individualToken, individualChannelID);
					if (success) {
						openSingleAccount = false;
					}
				}}
			>
				Add account
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<Dialog.Root bind:open={openBulkAccounts}>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>Add Bulk Accounts</Dialog.Title>
			<Dialog.Description>
				Select a text file that contains your discord tokens and channel ID's (optional). Each
				account should be on a separate line.
			</Dialog.Description>
		</Dialog.Header>
		<div class="grid gap-4 py-4">
			<div class="grid grid-cols-4 items-center gap-4">
				<Label class="text-right">Format</Label>
				<Select.Root type="single" bind:value={format.value}>
					<Select.Trigger class="col-span-3">Choose account format</Select.Trigger>
					<Select.Content>
						<Select.Item value="token">token</Select.Item>
						<Select.Item value="&quot;token&quot;">"token"</Select.Item>
						<Select.Item value="token id">token id</Select.Item>
						<Select.Item value="id token">id token</Select.Item>
						<Select.Item value="token: id">token: id</Select.Item>
						<Select.Item value="id: token">id: token</Select.Item>
					</Select.Content>
				</Select.Root>
			</div>
			<div class="grid grid-cols-4 items-center gap-4">
				<Label for="accounts" class="text-right">Tokens</Label>
				<Input
					class="col-span-3 dark:file:text-white"
					id="accounts"
					type="file"
					onchange={handleFileChange}
				/>
			</div>
		</div>
		<Dialog.Footer>
			<Button type="submit" onclick={() => (openBulkAccounts = false)}>Close</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
