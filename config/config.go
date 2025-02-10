package config

import (
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

type DelaySeconds struct {
	MinSeconds float32 `json:"minSeconds"`
	MaxSeconds float32 `json:"maxSeconds"`
}

type DelayMinutes struct {
	MinMinutes float32 `json:"minMinutes"`
	MaxMinutes float32 `json:"maxMinutes"`
}

type DelayHours struct {
	MinHours float32 `json:"minHours"`
	MaxHours float32 `json:"maxHours"`
}

type Cooldowns struct {
	ButtonClickDelay DelaySeconds `json:"buttonClickDelay"`
	CommandInterval  DelaySeconds `json:"commandInterval"`
	BreakCooldown    DelayHours   `json:"breakCooldown"`
	BreakDuration    DelayHours   `json:"breakDuration"`
	StartDelay       DelayMinutes `json:"startDelay"`
	EventDelay       DelaySeconds `json:"eventDelay"`
}

type Config struct {
	State               bool               `json:"state"`
	ApiKey              string             `json:"apiKey"`
	Gui                 GuiConfig          `json:"gui"`
	ReadAlerts          bool               `json:"readAlerts"`
	DiscordStatus       types.OnlineStatus `json:"discordStatus"`
	EventsCorrectChance float32            `json:"eventsCorrectChance"`
	Cooldowns           Cooldowns          `json:"cooldowns"`
	Accounts            []AccountsConfig   `json:"accounts"`
	AutoBuy             AutoBuyConfig      `json:"autoBuy"`
	AutoUse             AutoUseConfig      `json:"autoUse"`
	Commands            CommandsConfig     `json:"commands"`
	Adventure           AdventureConfig    `json:"adventure"`
}
