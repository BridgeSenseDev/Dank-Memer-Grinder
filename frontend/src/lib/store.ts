import { writable } from "svelte/store";
import { main, config } from "./wailsjs/go/models";
import { UpdateConfig } from "./wailsjs/go/main/App";

export const cfg = writable(new config.Config());

export const importantLogs = writable("");
export const othersLogs = writable("");
export const discordLogs = writable("");
export const logsEventListenersSet = writable(false);
export const layoutEventListenersSet = writable(false);

export const instances = writable<main.InstanceView[]>([]);

cfg.subscribe((newConfig) => {
	if (typeof newConfig.gui !== "undefined" && newConfig.gui.theme !== "") {
		UpdateConfig(newConfig);
	}
});
