package config

type AdventureConfig struct {
    Space map[string]string `json:"space"`
    West map[string]string `json:"west"`
    Brazil map[string]string `json:"brazil"`
    Vacation map[string]string `json:"vacation"`
}