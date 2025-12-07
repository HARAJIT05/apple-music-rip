# Apple Music Downloader Web UI

A simple, user-friendly web interface which works sometime for the Apple Music Downloader, allowing you to easily download high-quality audio from Apple Music.

## 🎵 About

This project serves as a graphical frontend for the powerful command-line tools developed by the community. It provides a clean, browser-based UI to search, configure, and download tracks without needing to interact with the terminal directly.

**Powered by:**
- **[zhaarey/apple-music-downloader](https://github.com/zhaarey/apple-music-downloader)** - The core Go-based downloader.
- **[WorldObservationLog/wrapper](https://github.com/WorldObservationLog/wrapper)** - The Android emulation wrapper for authentication (forked/based on **[zhaarey/wrapper](https://github.com/zhaarey/wrapper)**).

## ✨ Features

- **🌐 Web Interface**: Modern, responsive UI accessible from any browser.
- **🔐 Auto-Login**: Securely handles credentials and session management.
- **🎵 Multiple Formats**: Support for **ALAC** (Lossless), **AAC**, and **Dolby Atmos** (Spatial Audio).
- **📊 Real-time Monitoring**: Live logs for download progress and wrapper status.
- **⚙️ Complete Control**: Configure all downloader settings (quality, file naming, lyrics, etc.) via the UI.
- **🛠️ Self-Bootstrapping**: Automated setup script handles dependencies and compilation.

## 🚀 Quick Start

### Prerequisites
- **Linux** (x86_64 or aarch64) - Designed for Linux environments (including WSL).
- **Root/Sudo Access** - Required for the initial setup script to install dependencies.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/HARAJIT05/apple-music-rip.git
    cd alac-rip
    ```

2.  **Run the setup script:**
    ```bash
    sudo python3 main.py
    ```
    
    This script will automatically:
    - Install the **Nix** package manager (if missing) to create a reproducible environment.
    - Download the **Android NDK** and compile the necessary **Wrapper** tool.
    - Clone the **Apple Music Downloader** repository.
    - Start the Web UI.

3.  **Access the UI:**
    Open your web browser and navigate to: `http://localhost:5000`

## 📖 Usage

### Initial Setup
1.  **Login**: On the dashboard, click **"Login to Wrapper"**.
2.  **Status**: Monitor the logs for a successful login message (e.g., `[.] response type 6` or similar success indicators).

### Getting Your Media User Token
If the automatic login doesn't work or if you need to manually configure the token in **Settings**:

1.  Open [music.apple.com](https://music.apple.com) in your web browser and log in.
2.  Open **Developer Tools** (Press `F12` or right-click > Inspect).
3.  Navigate to the **Application** tab (or **Storage** tab in Firefox).
4.  Expand **Cookies** and select `https://music.apple.com`.
5.  Find the cookie named `media-user-token`.
6.  Copy its **Value** (it looks like a long string starting with `At...`).
7.  Paste this value into the **Media User Token** field in the Web UI **Settings**.

### Downloading Music
1.  **Select Format**: Choose between **AAC**, **ALAC** (Lossless), or **Atmos** (Spatial Audio).
    - *Note: For Atmos or ALAC, ensure "Special Audio" or relevant quality settings are enabled.*
2.  **Paste URL**: Enter an Apple Music album, playlist, or song URL.
3.  **Download**: Hit the download button and watch the progress in the logs.

## 📝 Changelog

### Recent Updates
- **UI Overhaul**: The "Special Audio" checkbox and separate format selectors have been unified into a single **Audio Quality** group for better clarity.
- **Hi-Res Support**: Added a dedicated **Hi-Res Lossless** option. This automatically configures the downloader to fetch higher quality manifests when available.
- **Smart Configuration**: The backend now dynamically updates the `get-m3u8-mode` setting based on your selection (switching between `web` for standard/AAC/Atmos and `hires` for Hi-Res), streamlining the download process.
- **Atmos Warnings**: Added UI alerts for Dolby Atmos mode to inform users about potential availability issues.

## ⚠️ Disclaimer
This tool is intended for **educational purposes and personal archiving only**. You must have a legal right to access the content you download. Please respect Apple's Terms of Service and copyright laws. The developers of this interface and the underlying tools are not responsible for any misuse.

## 🙏 Acknowledgments & Credits

This project stands on the shoulders of giants. A massive thank you to:

- **[@zhaarey](https://github.com/zhaarey)**: The original creator of the [Apple Music Downloader](https://github.com/zhaarey/apple-music-downloader) and the [Wrapper](https://github.com/zhaarey/wrapper). Their work is the foundation of this entire project.
- **[WorldObservationLog](https://github.com/WorldObservationLog)**: For maintaining the active [wrapper fork](https://github.com/WorldObservationLog/wrapper) used in this build.
- **[lalit22km](https://github.com/lalit22km)**: For creating [allac-rip](https://github.com/lalit22km/alac-rip) the tool for debain based system which is the core foundation for this project. 
- **[@HARAJIT05](https://github.com/harajit05)**: For creating this tool which collects all the packages and run the program in one go and make it universal for linux distros via **[Nix-Package-Manager](https://nixos.org/download/)**.
- The open-source community for their continuous research and contributions to digital audio preservation.
