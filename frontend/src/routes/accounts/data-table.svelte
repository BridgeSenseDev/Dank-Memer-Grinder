<script lang="ts">
	import { type ColumnDef, getCoreRowModel } from "@tanstack/table-core";
	import { createSvelteTable, FlexRender } from "$lib/components/ui/data-table/index.js";
	import { LockClosed, ExclamationTriangle, Check } from "svelte-radix";
	import * as Table from "$lib/components/ui/table/index.js";
	import { Button } from "$lib/components/ui/button";
	import type { Account } from "@/src/routes/accounts/columns";
	import AddAccounts from "./add-accounts.svelte";
	import { Input } from "$lib/components/ui/input";
	import { Checkbox } from "$lib/components/ui/checkbox";
	import {
		RestartInstances,
		UpdateInstanceToken
	} from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";
	import { cfg, instances } from "$lib/state.svelte";
	import {
		HourglassIcon,
		InfinityIcon,
		LoaderCircle,
		LoaderIcon,
		PauseIcon,
		Play,
		TerminalIcon
	} from "lucide-svelte";
	import { Label } from "$lib/components/ui/label";

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

	let isRestarting = $state(false);
	async function restartAllBots() {
		isRestarting = true;
		await RestartInstances();
		isRestarting = false;
	}

	function formatTimeRemaining(time?: string) {
		if (!time) {
			return "";
		}

		const diff = new Date(time).getTime() - new Date().getTime();
		if (diff > 0) {
			return (diff / 1000 / 60 / 60).toFixed(2);
		} else {
			return "0.00";
		}
	}

	$effect(() => {
		if (instances && cfg.c.accounts) {
			cfg.c.accounts.map((account) => {
				const instance = instances.i.find(
					(instance) => instance.accountCfg.token === account.token
				);
				const status = instance?.state ? instance.state : "initial";
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
									<Table.Cell class="w-18 p-0 text-center">
										{#if cell.getValue() === "ready"}
											<div class="flex flex-col items-center justify-center">
												<Check class="text-primary h-5 w-5" />
												<Label class="text-xs leading-4">Ready</Label>
											</div>
										{:else if cell.getValue() === "invalidToken"}
											<div class="flex flex-col items-center justify-center">
												<LockClosed class="h-5 w-5 text-red-500" />
												<Label class="text-xs leading-4">Token</Label>
											</div>
										{:else if cell.getValue() === "invalidChannelID"}
											<div class="flex flex-col items-center justify-center">
												<ExclamationTriangle class="h-5 w-5 text-yellow-500" />
												<Label class="text-xs leading-4">Channel ID</Label>
											</div>
										{:else if cell.getValue() === "initial"}
											<div class="flex flex-col items-center justify-center">
												<LoaderCircle class="h-5 w-5 animate-spin" />
												<Label class="text-xs leading-4">Waiting</Label>
											</div>
										{:else if cell.getValue() === "waitingUnready"}
											<div class="flex flex-col items-center justify-center">
												<LoaderCircle class="h-5 w-5 animate-spin" />
												<Label class="text-xs leading-4">Waiting</Label>
											</div>
										{:else if cell.getValue() === "restarting"}
											<div class="flex flex-col items-center justify-center">
												<LoaderIcon class="h-5 w-5 animate-spin" />
												<Label class="text-xs leading-4">Restarting</Label>
											</div>
										{:else if cell.getValue() === "waitingReady" && cfg.c.accounts && instances.findInstance(cfg.c.accounts[rowIndex].token)?.breakUpdateTime}
											<div class="flex flex-col items-center justify-center">
												<HourglassIcon class="h-5 w-5" />
												<Label class="text-xs leading-4">
													Left: {formatTimeRemaining(
														instances.findInstance(cfg.c.accounts[rowIndex].token)?.breakUpdateTime
													) ?? "0.00"}h
												</Label>
											</div>
										{:else if cell.getValue() === "running" && cfg.c.accounts && instances.findInstance(cfg.c.accounts[rowIndex].token)?.breakUpdateTime}
											<div class="flex flex-col items-center justify-center">
												<TerminalIcon class="text-primary h-5 w-5" />
												<Label class="text-xs leading-4">
													{#if cfg.c.cooldowns.breakDuration.minHours === 0 && cfg.c.cooldowns.breakDuration.maxHours === 0}
														<div class="flex flex-row items-center">
															Left:
															<InfinityIcon class="ml-1 h-4 w-4" />
														</div>
													{:else}
														Left: {formatTimeRemaining(
															instances.findInstance(cfg.c.accounts[rowIndex].token)
																?.breakUpdateTime
														) ?? "0.00"}h
													{/if}
												</Label>
											</div>
										{:else if cell.getValue() === "sleeping" && cfg.c.accounts && instances.findInstance(cfg.c.accounts[rowIndex].token)?.breakUpdateTime}
											<div class="flex flex-col items-center justify-center">
												<PauseIcon class="h-5 w-5 text-orange-500" />
												<Label class="text-xs leading-4">
													For {formatTimeRemaining(
														instances.findInstance(cfg.c.accounts[rowIndex].token)?.breakUpdateTime
													) ?? "0.00"}h
												</Label>
											</div>
										{:else if cell.getValue() === "starting"}
											<div class="flex flex-col items-center justify-center">
												<Play class="h-5 w-5 text-green-500" />
												<Label class="text-xs leading-4">Starting</Label>
											</div>
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
										<Input type="text" bind:value={cfg.c.accounts[rowIndex].channelID}></Input>
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
	<Button class="sticky text-base font-semibold" disabled={isRestarting} onclick={restartAllBots}>
		{#if isRestarting}
			<LoaderCircle class="animate-spin" /> Restarting...
		{:else}
			Restart all accounts
		{/if}
	</Button>
</div>
