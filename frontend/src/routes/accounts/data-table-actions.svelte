<script lang="ts">
	import { Trash, Reload } from "svelte-radix";
	import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
	import { Button } from "$lib/components/ui/button";
	import { cfg } from "$lib/state.svelte";
	import {
		RemoveInstance,
		RestartInstance
	} from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";
	import { Ellipsis } from "lucide-svelte";

	interface Props {
		id: string;
	}

	let { id }: Props = $props();

	async function deleteInstance(token: string) {
		RemoveInstance(token);
		if (cfg.c.accounts) {
			cfg.c.accounts = cfg.c.accounts.filter((account) => account.token !== token);
		}
	}
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="ghost" size="icon" class="relative size-8 p-0">
				<span class="sr-only">Open menu</span>
				<Ellipsis class="size-4" />
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content>
		<DropdownMenu.Group>
			<DropdownMenu.Item onclick={async () => await RestartInstance(id)}>
				<Reload class="mr-2 inline-block h-5 w-5" />
				Restart account
			</DropdownMenu.Item>
			<DropdownMenu.Separator />
			<DropdownMenu.Item
				class="text-red-500 hover:text-red-500"
				onclick={async () => await deleteInstance(id)}
			>
				<Trash class="mr-2 inline-block h-5 w-5" />Delete account</DropdownMenu.Item
			>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>
