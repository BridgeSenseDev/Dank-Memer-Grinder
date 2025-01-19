---
description: >-
  Build DMG yourself from source code. This is only recommended for people who
  don't have access to binaries or packages, or for developers who want to
  contribute to DMG.
---

# Build from Source

## Requirements

To build DMG, you need [Git](https://git-scm.com/), [Go v1.23](https://go.dev/) and [Bun](https://bun.sh/) installed:

### Git

Follow [this](https://github.com/git-guides/install-git) guide by GitHub to install git for your OS.

### Go

Follow the official [Go Installation Instructions](https://go.dev/doc/install) for your OS.

You will also need to ensure that your `PATH` environment variable also includes the path to your `~/go/bin` directory. Fully close and restart your terminal and do the following checks:

* Check Go is installed correctly: `go version`
* Check `~/go/bin` is in your PATH variable
  * Mac / Linux: `echo $PATH | grep go/bin`
  * Windows: `$env:PATH -split ';' | Where-Object { $_ -like '*\go\bin' }`

### Bun

macOS / Linux:

```sh
curl -fsSL https://bun.sh/install | bash
```

Windows:

```sh
powershell -c "irm bun.sh/install.ps1|iex"
```

To check that Bun was installed successfully, open a new terminal window and run `bun --version`

## Setting up

1. Begin by cloning the DMG repository and changing into the directory:

```sh
git clone https://github.com/BridgeSenseDev/Dank-Memer-Grinder.git
cd Dank-Memer-Grinder
```

2. Download and setup [Wails v3](https://v3alpha.wails.io/):

```sh
git clone https://github.com/wailsapp/wails.git
cd wails
git checkout v3-alpha
cd v3/cmd/wails3
go install
```

3. Check if you have all dependencies setup correctly:

```sh
wails3 doctor
```

4. Return to root project directory and install go dependencies:

```sh
cd ../../../../
go mod tidy
```

## Run the app

### Build

If you don't intend to make any changes and want to build an optimized binary:

```sh
// Windows
wails3 task windows:build

// Linux
wails3 task linux:package

// macOS
wails3 task darwin:build
```

After completing, find the binary in `Dank-Memer-Grinder/bin` .

### Dev

We can also run DMG in development mode. This mode allows you to make changes to code and see the changes reflected in the running application without having to rebuild the entire application:

```sh
wails3 dev
```
