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
import {
	GetConfig,
	UpdateConfig
} from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/dmgservice";
import { Browser } from "@wailsio/runtime";
import { OnlineStatus } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types";
import type { View } from "@/bindings/github.com/BridgeSenseDev/Dank-Memer-Grinder/instance";

(window as any).Browser = Browser;

class Cfg {
	c: Config = $state({
		state: false,
		apiKey: "",
		gui: {} as GuiConfig,
		readAlerts: false,
		discordStatus: "" as OnlineStatus,
		eventsCorrectChance: 0.65,
		cooldowns: {} as Cooldowns,
		accounts: [] as AccountsConfig[] | null,
		autoBuy: {} as AutoBuyConfig,
		autoUse: {} as AutoUseConfig,
		commands: {} as CommandsConfig,
		adventure: {} as AdventureConfig
	});

	constructor() {
		$effect.root(() => {
			$effect(() => {
				if (this.c.discordStatus !== "") {
					UpdateConfig(this.c);
				}
			});
		});

		Events.On("configUpdate", (data: { data: [newCfg: Config] }) => {
			this.c = data.data[0];
		});

		this.fetch();
	}

	async fetch() {
		const cfg = await GetConfig();
		if (cfg) {
			this.c = cfg;
		}
	}
}

class Instances {
	i = $state<View[]>([]);

	constructor() {
		Events.On("instanceUpdate", (data: { data: [newInstance: View] }) => {
			const instance = this.findInstance(data.data[0].accountCfg.token);
			if (instance) {
				instances.i[this.findInstanceIndex(data.data[0].accountCfg.token)] = data.data[0];
			} else {
				this.i.push(data.data[0]);
			}
		});
	}

	findInstanceIndex = (token: string) => {
		return this.i.findIndex((instance) => instance.accountCfg.token === token);
	};

	findInstance = (token: string) => {
		return this.i.find((instance) => instance.accountCfg.token === token);
	};
}

export type LogEntry = {
	level: string;
	type: string;
	username: string;
	message: string;
	timestamp: string;
	id: number;
};

class Logs {
	importantLogs = $state<LogEntry[]>([]);
	othersLogs = $state<LogEntry[]>([]);
	discordLogs = $state<LogEntry[]>([]);
	nextId = 0;

	constructor() {
		Events.On(
			"log",
			(data: { data: [level: string, logType: string, username: string, msg: string] }) => {
				const level = data.data[0];
				const logType = data.data[1];
				const username = data.data[2];
				const msg = data.data[3];

				const logEntry = this.createLogEntry(level, logType, username, msg);

				switch (level) {
					case "important":
						this.addLogEntry(this.importantLogs, logEntry);
						break;
					case "others":
						this.addLogEntry(this.othersLogs, logEntry);
						break;
					case "discord":
						this.addLogEntry(this.discordLogs, logEntry);
						break;
				}
			}
		);
	}

	private createLogEntry(level: string, type: string, username: string, msg: string): LogEntry {
		const now = new Date();
		const hours = now.getHours();
		const minutes = now.getMinutes();
		const ampm = hours >= 12 ? "PM" : "AM";
		const formattedTime = `${hours % 12 || 12}:${minutes < 10 ? "0" : ""}${minutes}${ampm}`;

		const processedMsg = msg.replace(
			/\[([^\]]+)]\((https?:\/\/[^)]+)\)/g,
			`<a href="#" onclick="event.preventDefault(); if(window.Browser && window.Browser.OpenURL){ window.Browser.OpenURL('$2'); } return false;" class="underline text-blue-500">$1</a>`
		);

		return {
			level,
			type,
			username,
			message: processedMsg,
			timestamp: formattedTime,
			id: this.nextId++
		};
	}

	private addLogEntry(logArray: LogEntry[], entry: LogEntry) {
		logArray.push(entry);
	}
}

export const cfg = $state(new Cfg());
export const instances = $state(new Instances());
export const logs = $state(new Logs());
