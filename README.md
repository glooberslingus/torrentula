# torrent-search

A minimal tool for finding open-source software and other freely
distributable torrents. Searches two sources in parallel:

- **apibay.org** — The Pirate Bay's official JSON API
- **api.knaben.org** — a meta-search API that itself aggregates TPB, 1337x,
  Nyaa, YTS, and other indexes

Results from both are merged, deduplicated, and sorted by seeder count so
the fastest option floats to the top.

## Project layout

```
torrent-search/
├── src/                    the actual app
│   ├── torrent_search.py
│   └── requirements.txt
├── icon/
│   └── torrent_search.ico  app icon (used when building the .exe)
├── build_exe.bat           Windows: builds dist\TorrentSearch.exe
├── install.bat              Windows: installs the built .exe (Start Menu + Programs list)
├── install.ps1               (called by install.bat)
└── dev_setup.py             optional: run from source instead of building an .exe
```

## Windows: build a real installed app (recommended)

This gets you a proper `TorrentSearch.exe` with its own icon, a Start Menu
entry, and a listing under **Settings > Apps > Installed apps** that you
can uninstall from there like any other program. No admin rights needed —
everything installs per-user.

**Step 1 — build the .exe.** Double-click `build_exe.bat` (or run it from a
terminal). This needs Python installed, but only temporarily, to run
[PyInstaller](https://pyinstaller.org/) — it creates a throwaway build
environment, compiles `dist\TorrentSearch.exe`, and cleans up after itself.
Takes a minute or two.

**Step 2 — install it.** Double-click `install.bat`. This copies
`TorrentSearch.exe` to `%LOCALAPPDATA%\Programs\TorrentSearch`, creates a
"Torrent Search" Start Menu shortcut, and registers it in Windows' Programs
list.

**Step 3 — use it.** Launch "Torrent Search" from the Start Menu, or run
the exe directly. Saved magnet files land in a `magnetfiles` folder next
to the installed exe.

To uninstall later: **Settings > Apps > Installed apps > Torrent Search >
Uninstall** (or Control Panel > Programs and Features).

Since this is an unsigned, locally-built exe, Windows SmartScreen may warn
you the first time you run it — that's expected for any app that isn't
purchased through a code-signing certificate; click "More info" > "Run
anyway" if you're comfortable doing so (you built it yourself, from the
source right here).

## Alternative: run from source (any OS)

If you'd rather not build an `.exe` — e.g. on macOS/Linux, or just to try
it quickly — run the installer once:

```bash
python dev_setup.py
```

It creates a local virtual environment inside this folder (nothing
system-wide), a `magnetfiles/` folder, and launcher scripts, then deletes
itself.

```bash
# Windows
run.bat "ubuntu 24.04 desktop"

# macOS/Linux
./run.sh "ubuntu 24.04 desktop"
```

### Windows-specific notes for source mode

Run it from a terminal (PowerShell or Command Prompt), not by
double-clicking `.py` files — that way you can see any output/errors
instead of the window closing instantly. If `python` isn't recognized, try
`py` instead.

The app forces UTF-8 output, so non-English torrent titles won't crash
older Windows consoles. If something does go wrong, it prints the full
error and waits for you to press Enter before closing, so you can read (or
copy) it.

## Use

You'll see a ranked list like:

```
#     S     L      Size  Source       Name
----------------------------------------------------------------------
1   842    31    5.7GB  PirateBay    ubuntu-24.04-desktop-amd64.iso
2   210     8    5.7GB  1337x        Ubuntu 24.04 LTS Desktop
...
```

Pick a number, then choose to:
1. **Copy the magnet link to your clipboard** (recommended) — paste it into
   your torrent client's "Add Link" / "Add Magnet Link" dialog
2. **Save it as a text file** in `magnetfiles/` — open the file, copy the
   link, and paste it the same way
3. Just print it, to copy manually

Important: a saved magnet file is plain text, **not** a real `.torrent`
file. Use your client's "Add Link"/"Add Magnet Link" option, not "Add
Torrent File" — the latter expects actual binary `.torrent` data and will
error out on a text file.

From there, open it in whatever torrent client you already use (qBittorrent,
Transmission, etc.) — this tool only searches and hands you the magnet
link; it doesn't download or manage torrents itself.

## Notes

- No API keys or accounts required.
- If a source is down or rate-limiting you, the tool reports it to stderr
  and keeps going with whatever the other source returned.
- `icon/make_icon.py` regenerates `torrent_search.ico` if you ever want to
  tweak the icon design (needs Pillow: `pip install pillow`). Not needed to
  build or run the app.
