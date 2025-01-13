import { browser } from "$app/environment";
import { Events } from "@wailsio/runtime";
import type {
	AccountsConfig,
	AdventureConfig,
	AutoBuyConfig,
	AutoUseConfig,
	CommandsConfig,
	Config,
	Cooldowns,
	GuiConfig
} from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/config";
import type { InstanceView } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder";
import {
	GetConfig,
	GetInstances,
	UpdateConfig
} from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";
import { OnlineStatus } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types";

class Cfg {
	c: Config = $state({
		state: false,
		apiKey: "",
		gui: {} as GuiConfig,
		readAlerts: false,
		discordStatus: "" as OnlineStatus,
		cooldowns: {} as Cooldowns,
		accounts: [] as AccountsConfig[] | null,
		autoBuy: {} as AutoBuyConfig,
		autoUse: {} as AutoUseConfig,
		commands: {} as CommandsConfig,
		adventure: {} as AdventureConfig
	});

	constructor() {
		if (browser) {
			$effect.root(() => {
				$effect(() => {
					if (this.c?.gui?.theme !== "") {
						UpdateConfig(this.c);
					}
				});
			});

			Events.On("configUpdate", (data: { data: [newCfg: Config] }) => {
				this.c = data.data[0];
			});

			this.fetch();
		}
	}

	async fetch() {
		if (browser) {
			const cfg = await GetConfig();
			if (cfg) {
				this.c = cfg;
			}
		}
	}
}

class Instances {
	i = $state<InstanceView[]>([]);

	constructor() {
		if (browser) {
			Events.On("instancesUpdate", (data: { data: [newInstances: InstanceView[]] }) => {
				this.i.length = 0;

				this.i.push(...data.data[0]);
			});

			this.fetch();
		}
	}

	async fetch() {
		if (browser) {
			const newInstances = await GetInstances();
			if (newInstances !== null) {
				this.i.length = 0;
				this.i.push(...(newInstances as InstanceView[]));
			}
		}
	}
}

class Logs {
	importantLogs = $state("");
	othersLogs = $state("");
	discordLogs = $state("");

	constructor() {
		if (browser) {
			Events.On("logImportant", (data: { data: [type: string, username: string, msg: string] }) => {
				const type = data.data[0];
				const username = data.data[1];
				const msg = data.data[2];

				this.importantLogs = this.logWithTime(this.importantLogs, type, username, msg);
			});

			Events.On("logOthers", (data: { data: [type: string, username: string, msg: string] }) => {
				const type = data.data[0];
				const username = data.data[1];
				const msg = data.data[2];

				this.othersLogs = this.logWithTime(this.othersLogs, type, username, msg);
			});

			Events.On("logDiscord", (data: { data: [type: string, username: string, msg: string] }) => {
				const type = data.data[0];
				const username = data.data[1];
				const msg = data.data[2];

				this.discordLogs = this.logWithTime(this.discordLogs, type, username, msg);
			});
		}
	}

	private logWithTime(logs: string, type: string, username: string, msg: string): string {
		const now = new Date();
		const hours = now.getHours();
		const minutes = now.getMinutes();
		const ampm = hours >= 12 ? "PM" : "AM";
		const formattedTime = `${hours % 12 || 12}:${minutes < 10 ? "0" : ""}${minutes}${ampm}`;

		logs += `<span class="text-gray-400">${formattedTime} `;

		if (type === "INF") {
			logs += `<span class="text-green-500">INF `;
		} else if (type === "ERR") {
			logs += `<span class="text-red-500">ERR `;
		}
		logs += `<span class="text-sky-500">` + username + '<span class="text-white"> ' + msg + "<br>";

		return logs;
	}
}

export const cfg = $state(new Cfg());
export const instances = $state(new Instances());
export const logs = $state(new Logs());
