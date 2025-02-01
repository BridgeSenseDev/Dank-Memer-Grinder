---
description: Explanation for settings found in DMG Settings
---

# General Settings

## Bot toggle

The DMG GUI has a global toggle switch for all accounts in the bottom left corner. This toggle switch is the fastest way to globally start or pause DMG. When off, all accounts will not send any commands or respond to messages.

## Auto read alerts

When on, automatically does `/alerts` when there are unread alerts to get rid of the annoying spam to read alerts.

## Discord status

Can be set to be either Online, Idle, Do not Disturb or Invisible. The status from any open Discord client overrides and has priority over this custom status.&#x20;



<details>

<summary>Auto Heist</summary>

### Auto Heist Channels

The Auto Heist Channels feature in Dank Memer Grinder allows you to set up specific channels where the bot will automatically join heists. To configure this functionality, follow these steps:

1. Locate the **"global"** settings section in `config.json`
2. Inside the **"global"** settings, find the **"autoheist"** section.
3. In the **"autoheist"** section, add your desired channel IDs. Make sure to separate each channel ID with commas.

{% code title="Example configuration" %}
```json
"autoheist": [12345678912345678, 12345678912345678, 12345678912345678]
```
{% endcode %}

### Default Auto Heist Order

{% code title="config.json" %}
```json
"autoheist": []
```
{% endcode %}

</details>
