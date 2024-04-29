package types

type User struct {
	ID            string `json:"id"`
	Username      string `json:"username"`
	Discriminator string `json:"discriminator"`
	Avatar        string `json:"avatar"`
	Bot           bool   `json:"bot,omitempty"`
	System        bool   `json:"system,omitempty"`
	MFAEnabled    bool   `json:"mfa_enabled,omitempty"`
	Locale        string `json:"locale,omitempty"`
	Verified      bool   `json:"verified,omitempty"`
	Email         string `json:"email,omitempty"`
	Status        string `json:"status,omitempty"`
}

type Guild struct {
	ID   string `json:"id"`
	Name string `json:"name"`

	Unavailable bool `json:"unavailable,omitempty"`
}

type Emoji struct {
	ID            string   `json:"id"`
	Name          string   `json:"name,omitempty"`
	Roles         []string `json:"roles,omitempty"`
	User          User     `json:"user,omitempty"`
	RequireColons bool     `json:"require_colons,omitempty"`
	Managed       bool     `json:"managed,omitempty"`
	Animated      bool     `json:"animated,omitempty"`
	Available     bool     `json:"available,omitempty"`
}

type Embed struct {
	Title       string                 `json:"title,omitempty"`
	Type        string                 `json:"type,omitempty"`
	Description string                 `json:"description,omitempty"`
	Timestamp   *string                `json:"timestamp,omitempty"`
	URL         string                 `json:"url,omitempty"`
	Image       *MessageEmbedImage     `json:"image,omitempty"`
	Color       int                    `json:"color,omitempty"`
	Footer      EmbedFooter            `json:"footer,omitempty"`
	Thumbnail   *MessageEmbedThumbnail `json:"thumbnail,omitempty"`
	Provider    EmbedProvider          `json:"provider,omitempty"`
	Author      EmbedAuthor            `json:"author,omitempty"`
	Fields      []EmbedField           `json:"fields,omitempty"`
}

type MessageEmbedImage struct {
	URL      string `json:"url,omitempty"`
	ProxyURL string `json:"proxy_url,omitempty"`
	Width    int    `json:"width,omitempty"`
	Height   int    `json:"height,omitempty"`
}

type EmbedField struct {
	Name   string `json:"name,omitempty"`
	Value  string `json:"value,omitempty"`
	Inline bool   `json:"inline,omitempty"`
}

type EmbedFooter struct {
	Text         string `json:"text,omitempty"`
	IconURL      string `json:"icon_url,omitempty"`
	ProxyIconURL string `json:"proxy_icon_url,omitempty"`
}

type EmbedAuthor struct {
	Name    string `json:"name,omitempty"`
	URL     string `json:"url,omitempty"`
	IconURL string `json:"icon_url,omitempty"`

	ProxyIconURL string `json:"proxy_icon_url,omitempty"`
}

type MessageEmbedThumbnail struct {
	URL      string `json:"url,omitempty"`
	ProxyURL string `json:"proxy_url,omitempty"`
	Width    int    `json:"width,omitempty"`
	Height   int    `json:"height,omitempty"`
}

type EmbedProvider struct {
	Name string `json:"name,omitempty"`
	URL  string `json:"url,omitempty"`
}

type Reaction struct {
	Emojis Emoji `json:"emoji,omitempty"`
	Count  int   `json:"count,omitempty"`
}

type MessageCheckFunc func(*MessageEventData) bool
