package config

import (
	"encoding/json"
	"os"
)

type DiscordStatus string

const (
	Online    DiscordStatus = "online"
	Idle      DiscordStatus = "idle"
	DND       DiscordStatus = "dnd"
	Invisible DiscordStatus = "invisible"
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
	State         bool             `json:"state"`
	ApiKey        string           `json:"apiKey"`
	Gui           GuiConfig        `json:"gui"`
	ReadAlerts    bool             `json:"readAlerts"`
	DiscordStatus DiscordStatus    `json:"discordStatus"`
	Cooldowns     Cooldowns        `json:"cooldowns"`
	Accounts      []AccountsConfig `json:"accounts"`
	AutoBuy       AutoBuyConfig    `json:"autoBuy"`
	Commands      CommandsConfig   `json:"commands"`
	Adventure     AdventureConfig  `json:"adventure"`
}

func ReadConfig(configFile string) (Config, error) {
	var config Config
	bytes, err := os.ReadFile(configFile)
	if err != nil {
		return config, err
	}
	err = json.Unmarshal(bytes, &config)
	return config, err
}
