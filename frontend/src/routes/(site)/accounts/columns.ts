import type { ColumnDef } from "@tanstack/table-core";
import { renderComponent } from "$lib/components/ui/data-table";
import DataTableActions from "@/src/routes/(site)/accounts/data-table-actions.svelte";

export interface Account {
	status: string;
	token: string;
	channelID: number;
	username: string;
	state: boolean;
}

export const columns: ColumnDef<Account>[] = [
	{
		accessorKey: "status",
		header: "Status"
	},
	{
		accessorKey: "username",
		header: "Username"
	},
	{
		accessorKey: "state",
		header: "State"
	},
	{
		accessorKey: "token",
		header: "Token"
	},
	{
		accessorKey: "channelID",
		header: "Channel ID"
	},
	{
		id: "actions",
		header: "Actions",
		cell: ({ row }) => {
			return renderComponent(DataTableActions, { id: row.original.token });
		}
	}
];
