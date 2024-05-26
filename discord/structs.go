package discord

// A TooManyRequests struct holds information received from Discord
// when receiving a HTTP 429 response.
type TooManyRequests struct {
	Bucket     string  `json:"bucket"`
	Message    string  `json:"message"`
	RetryAfter float64 `json:"retry_after"`
}
