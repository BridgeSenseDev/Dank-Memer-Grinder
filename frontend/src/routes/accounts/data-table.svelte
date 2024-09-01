<script lang="ts">
	import { createTable, Render, Subscribe, createRender } from "svelte-headless-table";
	import { LockClosed, ExclamationTriangle, Check, Update } from "svelte-radix";
	import { readable, writable } from "svelte/store";
	import * as Table from "$lib/components/ui/table";
	import DataTableActions from "./data-table-actions.svelte";
	import { cfg, instances } from "$lib/store";
	import { Checkbox } from "$lib/components/ui/checkbox";
	import { Input } from "$lib/components/ui/input";
	import { Button } from "$lib/components/ui/button";
	import * as Tooltip from "$lib/components/ui/tooltip/index.js";
	import { RestartInstances, UpdateInstanceToken } from "$lib/wailsjs/go/main/App";
	import AddAccounts from "./add-accounts.svelte";

	type Account = {
		status: string;
		token: string;
		channelID: number;
		username: string;
		state: boolean;
	};

	let accounts: Account[] = [];
	let tokenValues = writable(accounts.map((account) => account.token));
	let tableAttrs, headerRows, tableBodyAttrs, pageRows;

	const table = createTable(readable(accounts));

	const columns = table.createColumns([
		table.column({
			accessor: "status",
			header: "Status"
		}),
		table.column({
			accessor: "username",
			header: "Username"
		}),
		table.column({
			accessor: "state",
			header: "State"
		}),
		table.column({
			accessor: "token",
			header: "Token"
		}),
		table.column({
			accessor: "channelID",
			header: "Channel ID"
		}),
		table.column({
			accessor: ({ token }) => token,
			header: "",
			cell: ({ value }) => {
				return createRender(DataTableActions, { id: value });
			}
		})
	]);

	({ headerRows, pageRows, tableAttrs, tableBodyAttrs } = table.createViewModel(columns));

	$: {
		accounts = [];
		if ($instances && $cfg.accounts) {
			for (let account of $cfg.accounts) {
				let instance = $instances.find((instance) => instance.accountCfg.token === account.token);
				let status = instance?.error ? instance.error : "reload";
				accounts.push({
					status: status,
					token: account.token,
					channelID: parseInt(account.channelID, 10),
					username: instance?.user.username ?? "",
					state: account.state
				});
			}
		}

		if (accounts.length > 0) {
			const table = createTable(readable(accounts));
			({ headerRows, pageRows, tableAttrs, tableBodyAttrs } = table.createViewModel(columns));
		}
	}

	let hasChanges = false;
	function setHasChanges() {
		hasChanges = true;
	}

	async function restartAllBots() {
		await RestartInstances();
		hasChanges = false;
	}

	$: {
		tokenValues.set(accounts.map((account) => account.token));
	}

	function tokenUpdate(rowIndex: number, newToken: string) {
		if (newToken !== $cfg.accounts[rowIndex].token) {
			hasChanges = true;
			const oldToken = $cfg.accounts[rowIndex].token;
			UpdateInstanceToken(oldToken, newToken);
			$cfg.accounts[rowIndex].token = newToken;
			tokenValues.update((values) => {
				values[rowIndex] = newToken;
				return values;
			});
		}
	}

	let accountIndex = 0;
</script>

<div class="flex h-full flex-col justify-between">
	{#if $tableAttrs}
		<div>
			<div class="rounded-md rounded-b-none border border-b-0">
				<Table.Root {...$tableAttrs}>
					<Table.Header>
						{#each $headerRows as headerRow}
							<Subscribe rowAttrs={headerRow.attrs()}>
								<Table.Row>
									{#each headerRow.cells as cell (cell.id)}
										<Subscribe attrs={cell.attrs()} let:attrs props={cell.props()}>
											<Table.Head {...attrs}>
												<div class="text-center">
													<Render of={cell.render()} />
												</div>
											</Table.Head>
										</Subscribe>
									{/each}
								</Table.Row>
							</Subscribe>
						{/each}
					</Table.Header>
					<Table.Body {...$tableBodyAttrs}>
						{#each $pageRows as row, rowIndex (row.id)}
							<Subscribe rowAttrs={row.attrs()} let:rowAttrs>
								<Table.Row {...rowAttrs}>
									{#each row.cells as cell (cell.id)}
										<Subscribe attrs={cell.attrs()} let:attrs>
											{#if cell.id === "status"}
												<Table.Cell class="w-5 p-0 text-center" {...attrs}>
													{#if cell.value === "healthy"}
														<Tooltip.Root>
															<Tooltip.Trigger>
																<div class="flex items-center justify-center">
																	<Check class="text-primary" />
																</div></Tooltip.Trigger
															>
															<Tooltip.Content>Connected</Tooltip.Content>
														</Tooltip.Root>
													{:else if cell.value === "invalidToken"}
														<Tooltip.Root>
															<Tooltip.Trigger>
																<div class="flex items-center justify-center">
																	<LockClosed class="text-red-500" />
																</div></Tooltip.Trigger
															>
															<Tooltip.Content>Invalid token</Tooltip.Content>
														</Tooltip.Root>
													{:else if cell.value === "invalidChannelID"}
														<Tooltip.Root>
															<Tooltip.Trigger>
																<div class="flex items-center justify-center">
																	<ExclamationTriangle class="text-yellow-500" />
																</div></Tooltip.Trigger
															>
															<Tooltip.Content>Invalid channel ID</Tooltip.Content>
														</Tooltip.Root>
													{:else if cell.value === "reload"}
														<Tooltip.Root>
															<Tooltip.Trigger>
																<div class="flex items-center justify-center">
																	<Update class="text-orange-500" />
																</div></Tooltip.Trigger
															>
															<Tooltip.Content>Restart required</Tooltip.Content>
														</Tooltip.Root>
													{/if}
												</Table.Cell>
											{:else if cell.id === "state"}
												<Table.Cell class="p-0 text-center" {...attrs}>
													<Checkbox bind:checked={$cfg.accounts[rowIndex].state}></Checkbox>
												</Table.Cell>
											{:else if cell.id === "token"}
												<Table.Cell class="text-center" {...attrs}>
													<Input
														type="text"
														bind:value={$tokenValues[rowIndex]}
														on:input={(event) => tokenUpdate(rowIndex, event.target.value)}
													></Input>
												</Table.Cell>
											{:else if cell.id === "channelID"}
												<Table.Cell class="w-48 text-center" {...attrs}>
													<Input
														type="number"
														bind:value={$cfg.accounts[rowIndex].channelID}
														on:input={setHasChanges}
													></Input>
												</Table.Cell>
											{:else}
												<Table.Cell class="text-center" {...attrs}>
													<Render of={cell.render()} />
												</Table.Cell>
											{/if}
										</Subscribe>
									{/each}
								</Table.Row>
							</Subscribe>
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
			<AddAccounts />
		</div>
		<Button
			class={`sticky text-base font-semibold`}
			disabled={!hasChanges}
			on:click={restartAllBots}
		>
			Restart all accounts
		</Button>
	{:else}
		<h1>Nope</h1>
	{/if}
</div>
