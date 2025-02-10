<script lang="ts">
	import DataTable from "./data-table.svelte";
	import { columns } from "./columns";
	import { fade } from "svelte/transition";
	import { cfg, instances } from "$lib/state.svelte";

	let accounts = $derived.by(() => {
		const accounts = [];
		if (cfg.c.accounts) {
			for (const account of cfg.c.accounts) {
				const instance = instances.i.find(
					(instance) => instance.accountCfg.token === account.token
				);
				const status = instance?.state ? instance.state : "initial";
				accounts.push({
					status: status,
					token: account.token,
					channelID: parseInt(account.channelID, 10),
					username: instance?.user?.username ?? "",
					state: account.state
				});
			}
		}
		return accounts;
	});
</script>

<div
	in:fade={{ delay: 100, duration: 250 }}
	out:fade={{ duration: 100 }}
	class="flex h-full w-full flex-col"
>
	<DataTable data={accounts} {columns} />
</div>
