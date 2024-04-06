package types

type User struct {
	ID            string `json:"id"`
	Username      string `json:"username"`
	Discriminator string `json:"discriminator"`
	Avatar        string `json:"avatar"`
	Bot           bool   `json:"bot,omitempty"`
	System        bool   `json:"system,omitempty"`
	MFAEnabled    bool   `json:"mfa_enabled,omitempty"`
	Banner        string `json:"banner,omitempty"`
	AccentColor   int    `json:"accent_color,omitempty"`
	Locale        string `json:"locale,omitempty"`
	Verified      bool   `json:"verified,omitempty"`
	Email         string `json:"email,omitempty"`
	Flags         uint64 `json:"flag,omitempty"`
	PremiumType   uint64 `json:"premium_type,omitempty"`
	PublicFlags   uint64 `json:"public_flag,omitempty"`
	Status        string `json:"status,omitempty"`
}

type Guild struct {
	ID                          string        `json:"id"`
	Name                        string        `json:"name"`
	Icon                        string        `json:"icon"`
	IconHash                    string        `json:"icon_hash,omitempty"`
	Splash                      string        `json:"splash"`
	DiscoverySplash             string        `json:"discovery_splash"`
	Owner                       bool          `json:"owner,omitempty"`
	OwnerID                     string        `json:"owner_id"`
	Permissions                 string        `json:"permissions,omitempty"`
	Region                      string        `json:"region,omitempty"`
	AfkChannelID                string        `json:"afk_channel_id"`
	AfkTimeout                  int           `json:"afk_timeout"`
	WidgetEnabled               bool          `json:"widget_enabled,omitempty"`
	WidgetChannelID             string        `json:"widget_channel_id,omitempty"`
	VerificationLevel           uint64        `json:"verification_level"`
	DefaultMessageNotifications uint64        `json:"default_message_notifications"`
	ExplicitContentFilter       uint64        `json:"explicit_content_filter"`
	Roles                       []Role        `json:"roles"`
	Emojis                      []Emoji       `json:"emojis"`
	Features                    []string      `json:"features"`
	MFALevel                    uint64        `json:"mfa_level"`
	ApplicationID               string        `json:"application_id"`
	SystemChannelID             string        `json:"system_channel_id"`
	SystemChannelFlags          uint64        `json:"system_channel_flags"`
	RulesChannelID              string        `json:"rules_channel_id"`
	MaxPresences                int           `json:"max_presences,omitempty"`
	MaxMembers                  int           `json:"max_members,omitempty"`
	VanityUrl                   string        `json:"vanity_url_code"`
	Description                 string        `json:"description"`
	Banner                      string        `json:"banner"`
	PremiumTier                 uint64        `json:"premium_tier"`
	PremiumSubscriptionCount    int           `json:"premium_subscription_count,omitempty"`
	PreferredLocale             string        `json:"preferred_locale"`
	PublicUpdatesChannelID      string        `json:"public_updates_channel_id"`
	MaxVideoChannelUsers        int           `json:"max_video_channel_users,omitempty"`
	ApproximateMemberCount      int           `json:"approximate_member_count,omitempty"`
	ApproximatePresenceCount    int           `json:"approximate_presence_count,omitempty"`
	WelcomeScreen               WelcomeScreen `json:"welcome_screen,omitempty"`
	NSFWLevel                   uint64        `json:"nsfw_level"`
	Stickers                    []Sticker     `json:"stickers,omitempty"`
	PremiumProgressBarEnabled   bool          `json:"premium_progress_bar_enabled"`

	Unavailable bool `json:"unavailable,omitempty"`
}

type Role struct {
	ID           string   `json:"id"`
	Name         string   `json:"name"`
	Color        int      `json:"color"`
	Hoist        bool     `json:"hoist"`
	Icon         string   `json:"icon,omitempty"`
	UnicodeEmoji string   `json:"unicode_emoji,omitempty"`
	Position     int      `json:"position"`
	Permissions  string   `json:"permissions"`
	Managed      bool     `json:"managed"`
	Mentionable  bool     `json:"mentionable"`
	Tags         RoleTags `json:"tags,omitempty"`
}

type RoleTags struct {
	BotID             string `json:"bot_id,omitempty"`
	IntegrationID     string `json:"integration_id,omitempty"`
	PremiumSubscriber bool   `json:"premium_subscriber,omitempty"`
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

type WelcomeScreen struct {
	Description           string                 `json:"description"`
	WelcomeScreenChannels []WelcomeScreenChannel `json:"welcome_channels"`
}

type WelcomeScreenChannel struct {
	ChannelID   string `json:"channel_id"`
	Description string `json:"description"`
	EmojiID     string `json:"emoji_id"`
	EmojiName   string `json:"emoji_name"`
}

type Sticker struct {
	ID          string `json:"id"`
	PackID      string `json:"pack_id,omitempty"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Tags        string `json:"tags"`
	Asset       string `json:"asset,omitempty"`
	Type        uint64 `json:"type"`
	FormatType  uint64 `json:"format_type"`
	Available   bool   `json:"available,omitempty"`
	GuildID     string `json:"guild_id,omitempty"`
	User        User   `json:"user,omitempty"`
	SortValue   int    `json:"sort_value,omitempty"`
}

type Embed struct {
	Title       string                 `json:"title,omitempty"`
	Type        string                 `json:"type,omitempty"`
	Description string                 `json:"description,omitempty"`
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
