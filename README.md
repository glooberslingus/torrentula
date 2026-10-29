

Torrentula helps you find freely distributable torrents. The new graphical app is the main way to use it. It searches two sources in parallel, combines their results, removes duplicates, and ranks them by seeders.

## Install

1. Download and extract the ZIP.
2. Open the folder and run the installer for your computer:
   - **Windows:** double-click `Install-Windows.bat`
   - **macOS:** double-click `Install-macOS.command`
   - **Linux:** run `bash Install-Linux.sh` in a terminal
3. Open **Torrentula** from your Start Menu, Launchpad, or applications menu.

The installer sets up Torrentula for your user account, so administrator access is not needed. Python 3.8 or newer is needed during installation. Windows can install it automatically with winget; on macOS or Linux, the installer will explain how to get it if it is missing.

## Use the app

Enter a search or choose a suggestion. Select a result to view its details, then choose **Copy Magnet Link**, **Open in Client**, or **Save as File**. Torrentula only finds results and passes the magnet link to your torrent client; it does not download torrents.

The app follows your system's light or dark appearance. Use `/` to jump to search, the arrow keys to move through results, and **Show More Results** to load another page. If one search source is unavailable, Torrentula reports it and shows results from the other source when available.

## Terminal version

The terminal version is included as an alternative:

- **Windows:** open **Torrentula Terminal** from the Start Menu.
- **macOS/Linux:** run `torrentula "ubuntu 24.04"` in a terminal. You can also open the graphical app with `torrentula-gui`.

## Uninstall

- **Windows:** open **Settings > Apps > Installed apps**, select **Torrentula**, then choose **Uninstall**.
- **macOS:** run `files/macos/uninstall.command`.
- **Linux:** run `bash files/linux/uninstall.sh`.

Your saved magnet files are kept when you uninstall.

## If installation has a problem

- **Windows:** if SmartScreen appears, choose **More info > Run anyway** if you trust the ZIP you downloaded.
- **macOS:** if the installer is blocked, Control-click it, choose **Open**, then choose **Open** again.
- **Linux:** if Python's virtual environment cannot be created on Debian or Ubuntu, install it with `sudo apt install python3-venv` and run the installer again.

For more help, see the installer output. Torrentula searches apibay.org and api.knaben.org; no account or API key is required.
