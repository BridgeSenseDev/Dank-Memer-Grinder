---
description: Install DMG by downloading and running an optimized prebuilt binary.
---

# Pre-Built binaries

Download binaries for Windows, Linux and macOS from the [download page](https://dankmemer.tools/download). The correct version for your operating system should be automatically selected.

## Versions

### Alpha version

Click this option if you want the development version and help test the latest features. Report any bugs on our [Discord](https://discord.gg/KTrmQnhCHb).&#x20;

### Release version

Not out

## Running the downloaded binary

### Windows

{% hint style="warning" %}
You can run DMG by double clicking the .exe on Windows, but this is not recommended as you won't be able to see logs if DMG crashes.&#x20;
{% endhint %}

```bash
# GUI
.\dmg.exe

# CLI
.\dmg.exe -cli
```

### Linux

Find the package requirements for your distro below. After installed them, run the AppImage:

```bash
# GUI
./dmg-x86_64.AppImage

# CLI
./dmg-x86_64.AppImage -cli
```

#### **Debian and Ubuntu**

```bash
sudo apt install -y libfuse2 libgtk-3-dev libwebkit2gtk-4.1-dev
```

#### Fedora

```bash
sudo dnf install webkit2gtk4.1
```

#### Others

1. Follow [this guide](https://github.com/appimage/appimagekit/wiki/fuse) to install FUSE for your distro.
2. Install webkit2gtk4.1

### macOS

First, extract and double click the downloaded binary named `dmg` once. Because I'm not paying apple $100 a year to sign this app,  you must follow these instructions to allow the app to run:

1. From top left, choose Apple menu <picture><source srcset="../.gitbook/assets/apple_dark.svg" media="(prefers-color-scheme: dark)"><img src="../.gitbook/assets/apple.svg" alt="" data-size="line"></picture> > System Settings, then click Privacy & Security <img src="https://help.apple.com/assets/6716D93AEF41EE42B10D2617/6716D93E49B75650FD0A13E4/en_GB/f9979df145e31ea9fb18995403d2b2f6.png" alt="" data-size="line"> in the sidebar. (You may need to scroll down.)
2. Scroll down to Security section, where you should see `"dmg" was blocked to protect your mac`. Click `Open anyway`.
3. In the popup, click `Open anyway` again, then enter your login password, then click OK.

After installation, you can proceed to configuring DMG.

{% content-ref url="../configuration/getting-your-channel-id.md" %}
[getting-your-channel-id.md](../configuration/getting-your-channel-id.md)
{% endcontent-ref %}
