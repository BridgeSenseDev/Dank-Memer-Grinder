<script lang="ts">
	import { DotsVertical, Trash, Reload, DividerHorizontal } from "svelte-radix";
	import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
	import { Button } from "$lib/components/ui/button";
	import { RestartInstance, RemoveInstance } from "$lib/wailsjs/go/main/App";
	import { cfg } from "$lib/store";

	export let id: string;

	async function deleteInstance(token: string) {
		RemoveInstance(token);
		$cfg.accounts = $cfg.accounts.filter((account) => account.token !== token);
	}
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger asChild let:builder>
		<Button variant="ghost" builders={[builder]} size="icon" class="relative h-8 w-8 p-0">
			<span class="sr-only">Open menu</span>
			<DotsVertical class="h-4 w-4" />
		</Button>
	</DropdownMenu.Trigger>
	<DropdownMenu.Content>
		<DropdownMenu.Group>
			<DropdownMenu.Item on:click={async () => await RestartInstance(id)}>
				<Reload class="mr-2 inline-block h-5 w-5" />
				Restart account
			</DropdownMenu.Item>
			<DropdownMenu.Separator />
			<DropdownMenu.Item
				class="text-red-500 hover:text-red-500"
				on:click={async () => await deleteInstance(id)}
			>
				<Trash class="mr-2 inline-block h-5 w-5" />Delete account</DropdownMenu.Item
			>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>
