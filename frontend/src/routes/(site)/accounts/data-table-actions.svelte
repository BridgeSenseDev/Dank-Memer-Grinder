<script lang="ts">
	import { Trash, Reload } from "svelte-radix";
	import * as Tooltip from "$lib/components/ui/tooltip";
	import { Button } from "$lib/components/ui/button";
	import { cfg, instances } from "$lib/state.svelte.js";
	import {
		RemoveInstance,
		RestartInstance
	} from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";

	interface Props {
		id: string;
	}

	let { id }: Props = $props();

	async function deleteInstance(token: string) {
		RemoveInstance(token, false);
		// remove instance
		instances.i = instances.i.filter((instance) => instance.accountCfg.token !== token);
		if (cfg.c.accounts) {
			cfg.c.accounts = cfg.c.accounts.filter((account) => account.token !== token);
		}
	}
</script>

<div class="inline-flex flex-row space-x-2">
	<Tooltip.Provider>
		<Tooltip.Root>
			<Tooltip.Trigger>
				<Button variant="outline" size="icon" onclick={async () => await RestartInstance(id)}>
					<Reload />
				</Button>
			</Tooltip.Trigger>
			<Tooltip.Content>Restart</Tooltip.Content>
		</Tooltip.Root>
	</Tooltip.Provider>
	<Tooltip.Provider>
		<Tooltip.Root>
			<Tooltip.Trigger>
				<Button variant="destructive" size="icon" onclick={() => deleteInstance(id)}>
					<Trash />
				</Button>
			</Tooltip.Trigger>
			<Tooltip.Content>Delete</Tooltip.Content>
		</Tooltip.Root>
	</Tooltip.Provider>
</div>
