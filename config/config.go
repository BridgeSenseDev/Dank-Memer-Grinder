package config

import (
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

type Delays struct {
	MinDelay int `json:"minDelay"`
	MaxDelay int `json:"maxDelay"`
}

type Cooldowns struct {
	ButtonClickDelay Delays `json:"buttonClickDelay"`
	CommandInterval  Delays `json:"commandInterval"`
}

type Config struct {
	State         bool               `json:"state"`
	ApiKey        string             `json:"apiKey"`
	Gui           GuiConfig          `json:"gui"`
	ReadAlerts    bool               `json:"readAlerts"`
	DiscordStatus types.OnlineStatus `json:"discordStatus"`
	Cooldowns     Cooldowns          `json:"cooldowns"`
	Accounts      []AccountsConfig   `json:"accounts"`
	AutoBuy       AutoBuyConfig      `json:"autoBuy"`
	AutoUse       AutoUseConfig      `json:"autoUse"`
	Commands      CommandsConfig     `json:"commands"`
	Adventure     AdventureConfig    `json:"adventure"`
}
