package config

type AccountsConfig struct {
	Token     string `json:"token"`
	ChannelID string `json:"channelID"`
	State     bool   `json:"state"`
}