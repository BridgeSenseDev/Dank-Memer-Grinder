<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Plus, Person, MagicWand } from 'svelte-radix';
	import { Label } from '$lib/components/ui/label';
	import { Input } from '$lib/components/ui/input';
	import * as Select from '$lib/components/ui/select';
	import { Button } from '$lib/components/ui/button';
	import { cfg } from '$lib/store';

	let individualToken = '';
	let individualChannelID = '';

	function addAccount(token: string, channelID: string) {
		const updatedAccounts = [
			...$cfg.accounts,
			{
				token: token,
				channelID: channelID,
				state: false
			}
		];

		$cfg.accounts = updatedAccounts;
	}

	function handleFileChange(event: Event) {
		const input = event.target as HTMLInputElement;
		const files = input.files;
		if (files) {
			const file = files[0];
			const reader = new FileReader();

			reader.onload = (e) => {
				if (e.target !== null) {
					parseAndAddAccounts(e.target.result as string);
				}
			};

			reader.readAsText(file);
		}
	}

	function parseAndAddAccounts(fileContent: string) {
		const lines = fileContent.split('\n');

		lines.forEach((line) => {
			line = line.trim();

			switch (format.value) {
				case 'token':
					addAccount(line, '');
					break;
				case '"token"':
					const tokenMatch = line.match(/"(.*?)"/);
					if (tokenMatch) {
						addAccount(tokenMatch[1], '');
					}
					break;
				case 'token id':
					let parts = line.split(' ');
					if (parts.length >= 2) {
						addAccount(parts[0], parts[1]);
					}
					break;
				case 'id token':
					parts = line.split(' ');
					if (parts.length >= 2) {
						addAccount(parts[1], parts[0]);
					}
					break;
				case 'token: id':
					let colonParts = line.split(':');
					if (colonParts.length >= 2) {
						addAccount(colonParts[0].trim(), colonParts[1].trim());
					}
					break;
				case 'id: token':
					colonParts = line.split(':');
					if (colonParts.length >= 2) {
						addAccount(colonParts[1].trim(), colonParts[0].trim());
					}
					break;
			}
		});
	}

	let openSingleAccount = false;
	let openBulkAccounts = false;
	let format = { value: 'token id', label: 'token id' };
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger asChild let:builder>
		<Button class="w-full rounded-t-none border" variant="ghost" builders={[builder]}>
			<span class="sr-only">Actions</span>
			<Plus class="h-5" />
		</Button>
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="center">
		<DropdownMenu.Item on:click={() => (openSingleAccount = true)}
			><Person class="mr-1" /> Single account</DropdownMenu.Item
		>
		<DropdownMenu.Item
			on:click={() => (openBulkAccounts = true)}
			class="text-primary hover:text-primary"
		>
			<MagicWand class="mr-1" /> Bulk accounts
		</DropdownMenu.Item>
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
				<Input type="number" id="channelID" class="col-span-3" bind:value={individualChannelID} />
			</div>
		</div>
		<Dialog.Footer>
			<Button
				type="submit"
				on:click={() => {
					addAccount(individualToken, individualChannelID);
					openSingleAccount = false;
				}}>Save account</Button
			>
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
				<Select.Root selected={format}>
					<Select.Trigger class="col-span-3">
						<Select.Value placeholder="Choose account format" />
					</Select.Trigger>
					<Select.Content>
						<Select.Item value="token">token</Select.Item>
						<Select.Item value={`"token"`}>"token"</Select.Item>
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
					on:change={handleFileChange}
				/>
			</div>
		</div>
		<Dialog.Footer>
			<Button type="submit" on:click={() => (openBulkAccounts = false)}>Close</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
