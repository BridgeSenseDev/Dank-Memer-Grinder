<script lang="ts">
	import { type ColumnDef, getCoreRowModel } from "@tanstack/table-core";
	import { createSvelteTable, FlexRender } from "$lib/components/ui/data-table/index.js";
	import { LockClosed, ExclamationTriangle, Check } from "svelte-radix";
	import * as Table from "$lib/components/ui/table/index.js";
	import { Button } from "$lib/components/ui/button";
	import type { Account } from "@/src/routes/accounts/columns";
	import AddAccounts from "./add-accounts.svelte";
	import { Input } from "$lib/components/ui/input";
	import * as Tooltip from "$lib/components/ui/tooltip";
	import { Checkbox } from "$lib/components/ui/checkbox";
	import {
		RestartInstances,
		UpdateInstanceToken
	} from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";
	import { cfg, instances } from "$lib/state.svelte";
	import { LoaderCircle } from "lucide-svelte";

	interface DataTableProps<TData, TValue> {
		columns: ColumnDef<TData, TValue>[];
		data: TData[];
	}

	let { data, columns }: DataTableProps<Account, ColumnDef<Account>> = $props();

	const table = createSvelteTable({
		get data() {
			return data;
		},
		columns,
		getCoreRowModel: getCoreRowModel()
	});

	let hasChanges = $state(false);
	function setHasChanges() {
		hasChanges = true;
	}

	let isRestarting = $state(false);
	async function restartAllBots() {
		isRestarting = true;
		await RestartInstances();
		hasChanges = false;
		isRestarting = false;
	}

	$effect(() => {
		if (instances && cfg.c.accounts) {
			cfg.c.accounts.map((account) => {
				const instance = instances.i.find(
					(instance) => instance.accountCfg.token === account.token
				);
				const status = instance?.error ? instance.error : "reload";
				return {
					status,
					token: account.token,
					channelID: parseInt(account.channelID, 10),
					username: instance?.user?.username ?? "",
					state: account.state
				};
			});
		}
	});

	function tokenUpdate(rowIndex: number, event: Event) {
		const newToken = (event.target as HTMLInputElement).value;

		if (cfg.c.accounts && newToken !== cfg.c.accounts[rowIndex].token) {
			const oldToken = cfg.c.accounts[rowIndex].token;
			UpdateInstanceToken(oldToken, newToken);
			cfg.c.accounts[rowIndex].token = newToken;
			hasChanges = true;
		}
	}

	function changeState(rowIndex: number) {
		if (cfg.c.accounts) {
			cfg.c.accounts[rowIndex].state = !cfg.c.accounts[rowIndex].state;
		}
	}
</script>

<div class="flex h-full flex-col justify-between">
	<div>
		<div class="rounded-md rounded-b-none border border-b-0">
			<Table.Root>
				<Table.Header>
					{#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
						<Table.Row>
							{#each headerGroup.headers as header (header.id)}
								<Table.Head class="text-center">
									{#if !header.isPlaceholder}
										<FlexRender
											content={header.column.columnDef.header}
											context={header.getContext()}
										/>
									{/if}
								</Table.Head>
							{/each}
						</Table.Row>
					{/each}
				</Table.Header>
				<Table.Body>
					{#each table.getRowModel().rows as row, rowIndex (row.id)}
						<Table.Row data-state={row.getIsSelected() && "selected"}>
							{#each row.getVisibleCells() as cell (cell.id)}
								{#if cell.column.id === "status"}
									<Table.Cell class="w-5 p-0 text-center">
										{#if cell.getValue() === "healthy"}
											<Tooltip.Provider>
												<Tooltip.Root>
													<Tooltip.Trigger>
														<div class="flex items-center justify-center">
															<Check class="text-primary" />
														</div>
													</Tooltip.Trigger>
													<Tooltip.Content>Connected</Tooltip.Content>
												</Tooltip.Root>
											</Tooltip.Provider>
										{:else if cell.getValue() === "invalidToken"}
											<Tooltip.Provider>
												<Tooltip.Root>
													<Tooltip.Trigger>
														<div class="flex items-center justify-center">
															<LockClosed class="text-red-500" />
														</div>
													</Tooltip.Trigger>
													<Tooltip.Content>Invalid token</Tooltip.Content>
												</Tooltip.Root>
											</Tooltip.Provider>
										{:else if cell.getValue() === "invalidChannelID"}
											<Tooltip.Provider>
												<Tooltip.Root>
													<Tooltip.Trigger>
														<div class="flex items-center justify-center">
															<ExclamationTriangle class="text-yellow-500" />
														</div>
													</Tooltip.Trigger>
													<Tooltip.Content>Invalid channel ID</Tooltip.Content>
												</Tooltip.Root>
											</Tooltip.Provider>
										{:else if cell.getValue() === "reload"}
											<Tooltip.Provider>
												<Tooltip.Root>
													<Tooltip.Trigger>
														<div class="flex items-center justify-center">
															<LoaderCircle class="animate-spin" />
														</div>
													</Tooltip.Trigger>
													<Tooltip.Content>Loading</Tooltip.Content>
												</Tooltip.Root>
											</Tooltip.Provider>
										{/if}
									</Table.Cell>
								{:else if cell.column.id === "state" && cfg.c.accounts}
									<Table.Cell class="p-0 text-center">
										<Checkbox
											bind:checked={cfg.c.accounts[rowIndex].state}
											onchange={() => changeState(rowIndex)}
										></Checkbox>
									</Table.Cell>
								{:else if cell.column.id === "token" && cfg.c.accounts}
									<Table.Cell class="text-center">
										<Input
											type="text"
											bind:value={cfg.c.accounts[rowIndex].token}
											oninput={(event) => tokenUpdate(rowIndex, event)}
										></Input>
									</Table.Cell>
								{:else if cell.column.id === "channelID" && cfg.c.accounts}
									<Table.Cell class="w-48 text-center">
										<Input
											type="text"
											bind:value={cfg.c.accounts[rowIndex].channelID}
											oninput={setHasChanges}
										></Input>
									</Table.Cell>
								{:else}
									<Table.Cell class="text-center">
										<FlexRender content={cell.column.columnDef.cell} context={cell.getContext()} />
									</Table.Cell>
								{/if}
							{/each}
						</Table.Row>
					{:else}
						<Table.Row>
							<Table.Cell colspan={columns.length} class="h-24 text-center">No results.</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
		<AddAccounts />
	</div>
	<Button
		class="sticky text-base font-semibold"
		disabled={!hasChanges || isRestarting}
		onclick={restartAllBots}
	>
		{#if isRestarting}
			<LoaderCircle class="animate-spin" /> Restarting...
		{:else}
			Restart all accounts
		{/if}
	</Button>
</div>
