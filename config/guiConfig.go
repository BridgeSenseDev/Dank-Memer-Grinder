package config

type Theme string

const (
	System Theme = "system"
	Dark   Theme = "dark"
	Light Theme = "light"
)

type GuiConfig struct {
	Theme Theme `json:"theme"`
}