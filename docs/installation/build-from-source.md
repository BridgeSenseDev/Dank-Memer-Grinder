---
description: >-
  Build DMG yourself from source code. This is only recommended for people who
  don't have access to binaries or packages, or for developers who want to
  contribute to DMG.
---

# Build from Source

## Requirements

### Git

Follow [this](https://github.com/git-guides/install-git) guide by GitHub to install git for your OS.

### Go

Follow the official [Go Installation Instructions](https://go.dev/doc/install) for your OS.

You will also need to ensure that your `PATH` environment variable also includes the path to your `~/go/bin` directory.&#x20;

{% hint style="info" %}
`~/go/bin` is usually automatically added to path on Windows if you use the official installer. It will usually have to be done manually on Linux / macOS.
{% endhint %}

On Linux and macOS, copy and run this code block in terminal to do it automatically:

{% code title="Only Linux / macOS" overflow="wrap" %}
```bash
CURRENT_SHELL=$(echo $SHELL)
echo "Your current shell is: $CURRENT_SHELL"

PATH_LINE='export PATH=$PATH:$HOME/go/bin'

if [[ $CURRENT_SHELL == *"zsh"* ]]; then
    if ! grep -q "PATH=.*go/bin" ~/.zshrc; then
        echo $PATH_LINE >> ~/.zshrc
        source ~/.zshrc
        echo "Added to ~/.zshrc"
    else
        echo "go/bin already exists in ~/.zshrc"
    fi
elif [[ $CURRENT_SHELL == *"bash"* ]]; then
    if ! grep -q "PATH=.*go/bin" ~/.bashrc; then
        echo $PATH_LINE >> ~/.bashrc
        source ~/.bashrc
        echo "Added to ~/.bashrc"
    else
        echo "go/bin already exists in ~/.bashrc"
    fi
else
    echo "Unsupported shell: $CURRENT_SHELL. Find instructions yourself."
fi
```
{% endcode %}

Fully close and restart your terminal then do the following checks:

* Check Go is installed correctly: `go version`
* Check `~/go/bin` is in your PATH variable, the output from running these commands should not be empty:
  * Mac / Linux: `echo $PATH | grep go/bin`
  * Windows: `$env:PATH -split ';' | Where-Object { $_ -like '*\go\bin' }`

### Bun

macOS / Linux:

```bash
curl -fsSL https://bun.sh/install | bash
```

Windows:

```powershell
powershell -c "irm bun.sh/install.ps1|iex"
```

To check that Bun was installed successfully, open a new terminal window and run `bun --version`

## Setting up

1. Begin by cloning the DMG repository and changing into the directory:

```bash
git clone https://github.com/BridgeSenseDev/Dank-Memer-Grinder.git
cd Dank-Memer-Grinder
```

2. Install go dependencies:

```bash
go mod tidy
```

3. Install wails CLI:

```bash
go install -v github.com/wailsapp/wails/v3/cmd/wails3@latest
```

4. Run this command to check if you have the correct dependencies installed. If not, it will advise on what is missing and help on how to rectify any problems.

```sh
wails3 doctor
```

{% hint style="danger" %}
If you see something like `wails3: command not found...` make sure you've followed [these](build-from-source.md#go) previous instructions to add `/go/bin` to path correctly
{% endhint %}

## Build (Recommended)

If you don't intend to make any changes and want to build an optimized binary:

```sh
// Windows
wails3 task windows:build

// Linux
wails3 task linux:build

// macOS
wails3 task darwin:build
```

After completing, the binary will be located in `Dank-Memer-Grinder/bin` .

## Dev

We can also run DMG in development mode. This mode allows you to make changes to code and see the changes reflected in the running application without having to rebuild the entire application:

```sh
wails3 dev
```

After installation, you can proceed to configuring DMG.

{% content-ref url="../configuration/getting-your-channel-id.md" %}
[getting-your-channel-id.md](../configuration/getting-your-channel-id.md)
{% endcontent-ref %}
