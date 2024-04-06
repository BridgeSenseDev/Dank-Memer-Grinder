package discord

import (
	"github.com/BridgeSenseDev/Dank-Memer-Grinder/discord/types"
)

type Selfbot struct {
	Token string
	User  types.User
}

// A TooManyRequests struct holds information received from Discord
// when receiving a HTTP 429 response.
type TooManyRequests struct {
	Bucket     string  `json:"bucket"`
	Message    string  `json:"message"`
	RetryAfter float64 `json:"retry_after"`
}
