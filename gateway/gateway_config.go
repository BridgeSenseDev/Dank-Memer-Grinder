package gateway

import (
	"fmt"
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/config"
	"github.com/fasthttp/websocket"
)

// DefaultConfig returns a Config with sensible defaults.
func DefaultConfig() *Config {
	cfg, err := config.ReadConfig("config.json")
	if err != nil {
		panic(fmt.Sprintf("Failed to read config file: %s", err.Error()))
	}

	presence := MessageDataPresenceUpdate{
		Since:      new(int64),
		Activities: []map[string]interface{}{},
		Status:     cfg.DiscordStatus,
		AFK:        false,
	}

	return &Config{
		Dialer:          websocket.DefaultDialer,
		Compress:        true,
		URL:             "wss://gateway.discord.gg",
		AutoReconnect:   true,
		EnableResumeURL: true,
		RateLimiter:     NewRateLimiter(),
		Presence:        &presence,
		UserAgent:       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
	}
}

// Config lets you configure your Gateway instance.
type Config struct {
	// Dialer is the websocket.Dialer of the Gateway. Defaults to websocket.DefaultDialer.
	Dialer *websocket.Dialer
	// Compress is whether the Gateway should compress payloads. Defaults to true.
	Compress bool
	// URL is the URL of the Gateway. Defaults to fetch from Discord.
	URL string
	// SessionID is the last sessionID of the Gateway. Defaults to nil (no resume).
	SessionID *string
	// ResumeURL is the last resumeURL of the Gateway. Defaults to nil (no resume).
	ResumeURL *string
	// LastSequenceReceived is the last sequence received by the Gateway. Defaults to nil (no resume).
	LastSequenceReceived *int
	// AutoReconnect is whether the Gateway should automatically reconnect. Defaults to true.
	AutoReconnect bool
	// EnableRawEvents is whether the Gateway should emit EventRaw. Defaults to false.
	EnableRawEvents bool
	// EnableResumeURL is whether the Gateway should enable the resumeURL. Defaults to true.
	EnableResumeURL bool
	// RateLimiter is the RateLimiter of the Gateway. Defaults to NewRateLimiter().
	RateLimiter RateLimiter
	// RateLimiterConfigOpts is the RateLimiterConfigOpts of the Gateway. Defaults to nil.
	RateLimiterConfigOpts []RateLimiterConfigOpt
	// Presence is the presence it should send on login. Defaults to config value.
	Presence *MessageDataPresenceUpdate
	// UserAgent is the UserAgent it should send on login and on api requests
	UserAgent string
}
