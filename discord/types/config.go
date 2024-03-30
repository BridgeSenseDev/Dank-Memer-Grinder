package types

type Config struct {
	Presence       string
	ApiVersion     string
	Browser        string
	BrowserVersion string
	Capabilities   int64
	Device         string
	Os             string
	OsVersion      string
	UserAgent      string
}

var DefaultConfig = Config{
	Presence:       "online",
	ApiVersion:     "9",
	Browser:        "Chrome",
	BrowserVersion: "118.0.0.0",
	Capabilities:   4093,
	Device:         "",
	Os:             "Windows",
	OsVersion:      "10",
	UserAgent:      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
}
