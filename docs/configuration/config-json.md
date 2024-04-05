# Config.json Documentation

## Overview
The `config.json` file allows users to configure various settings for advanced usage. Below is a detailed explanation of each field and its purpose.

## Global Settings
| Field         | Type     | Default | Description                                          |
|---------------|----------|---------|------------------------------------------------------|
| `state`       | Boolean  | OFF     | Indicates the ON/OFF state of the application.      |
| `apiKey`      | String   | ""      | API key used for authentication.                     |
| `gui`         | Object   |         | Graphical user interface settings.                   |
|               | `theme`  | String  | "system"                                             |
| `readAlerts`  | Boolean  | ON      | Determines whether alerts are enabled for reading.   |
| `discordStatus`| String  | "idle"  | Specifies the status of the Discord integration.     |
| `accounts`    | Array    |         | Array of user account settings.                      |
|               | `token`  | String  | Authentication token for user accounts.              |
|               | `channelID`| String | ID of the channel associated with the user account. |
|               | `state`  | Boolean | ON                                                   |

## Auto Buy Settings
| Field         | Type     | Default | Description                                          |
|---------------|----------|---------|------------------------------------------------------|
| `autoBuy`     | Object   |         | Settings for automatic purchases.                    |
|               | `huntingRifle`| Object| Settings for hunting rifle purchase.                |
|               |           | `state` | Boolean | ON                                               |
|               |           | `amount`| Number  | 1                                                |
|               | `shovel` | Object   | Settings for shovel purchase.                        |
|               |           | `state` | Boolean | OFF                                              |
|               |           | `amount`| Number  | 1                                                |
|               | `lifeSavers`| Object| Settings for life savers purchase.                  |
|               |           | `state` | Boolean | ON                                               |
|               |           | `amount`| Number  | 1                                                |

## Command Settings
| Field         | Type     | Default | Description                                          |
|---------------|----------|---------|------------------------------------------------------|
| `commands`    | Object   |         | Settings for various commands.                       |
|               | `adventure`| Object| Settings for adventure command.                     |
|               |           | `state` | Boolean | OFF                                              |
|               |           | `delay` | Number  | 1800                                            |
|               |           | `adventureOption`| String | "west"                                       |
|               | `beg`    | Object   | Settings for beg command.                            |
|               |           | `state` | Boolean | OFF                                              |
|               |           | `delay` | Number  | 40                                              |
| Additional command settings are listed in the actual configuration file.

## Adventure Settings
| Field         | Type     | Description                                          |
|---------------|----------|------------------------------------------------------|
| `adventure`   | Object   | Settings specific to different adventure scenarios. |
| Specific settings for each adventure scenario are listed in the actual configuration file.

## Example
```json
{
  "state": true,
  "apiKey": "your_api_key",
  "gui": {
    "theme": "dark"
  },
  "readAlerts": true,
  "discordStatus": "online",
  "accounts": [
    {
      "token": "user_token_123",
      "channelID": "channel_456",
      "state": true
    }
  ],
  "autoBuy": {
    "huntingRifle": {
      "state": true,
      "amount": 2
    },
    "shovel": {
      "state": false,
      "amount": 1
    },
    "lifeSavers": {
      "state": true,
      "amount": 3
    }
  },
  "commands": {
    "adventure": {
      "state": true,
      "delay": 1800,
      "adventureOption": "west"
    },
    "beg": {
      "state": false,
      "delay": 40
    }
  },
  "adventure": {
    "west": {
      "A lady next to a broken down wagon is yelling for help.": "Help Her",
      "A stranger challenges you to a quick draw. What do you want to do?": "Accept the challenge"
    }
  }
}