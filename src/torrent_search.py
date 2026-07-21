#!/usr/bin/env python3
"""
torrent_search.py

A simple terminal torrent search tool. Queries multiple public torrent
indexes, merges and ranks the results by seeder count, and lets you either
copy the winning magnet link to your clipboard or save it as a text file in
/magnetfiles, for use in your own torrent client.

Intended for legal use: open-source software, Linux distros, and other
freely distributable files.

Usage:
    python torrent_search.py "ubuntu 24.04 desktop"
    python torrent_search.py            # will prompt for a search term
"""

import argparse
import os
import re
import subprocess
import sys
import shutil
import urllib.parse
from dataclasses import dataclass
from typing import List, Optional

import requests

# Windows consoles often default to a legacy codepage (cp1252/cp437) that
# can't print many characters that show up in torrent titles (accented
# letters, CJK text, symbols, etc.), which raises UnicodeEncodeError and
# crashes the script. Force UTF-8 output where possible; on older Python
# versions that don't support reconfigure(), just fall back silently.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

USER_AGENT = "Mozilla/5.0 (compatible; torrent-search-cli/1.0)"
TIMEOUT = 12

# Where saved .magnet files go. Relative to the app itself (not the current
# working directory), so it lands in the same place regardless of where you
# run the tool from. When frozen into an .exe by PyInstaller, __file__ points
# into a temporary extraction folder that gets wiped on exit, so we use the
# actual .exe's location instead in that case.
if getattr(sys, "frozen", False):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# run.bat/run.sh (dev/source mode) set this so magnetfiles ends up at the
# project root instead of inside src/, matching where dev_setup.py created it.
MAGNET_DIR = os.environ.get("TORRENT_SEARCH_MAGNET_DIR") or os.path.join(SCRIPT_DIR, "magnetfiles")


@dataclass
class Result:
    name: str
    seeders: int
    leechers: int
    size_bytes: int
    source: str
    magnet: str


# --------------------------------------------------------------------------
# Source: apibay.org (The Pirate Bay's official JSON API)
# --------------------------------------------------------------------------
def search_apibay(query: str) -> List[Result]:
    url = "https://apibay.org/q.php"
    try:
        resp = requests.get(
            url,
            params={"q": query, "cat": 0},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [apibay] search failed: {e}", file=sys.stderr)
        return []

    results = []
    for item in data:
        # apibay returns a single dummy entry {"id": "0", "name": "No results returned"}
        info_hash = item.get("info_hash", "")
        if not info_hash or item.get("id") == "0":
            continue
        name = item.get("name", "unknown")
        magnet = build_magnet(info_hash, name)
        try:
            seeders = int(item.get("seeders", 0))
            leechers = int(item.get("leechers", 0))
            size_bytes = int(item.get("size", 0))
        except (TypeError, ValueError):
            continue
        results.append(
            Result(
                name=name,
                seeders=seeders,
                leechers=leechers,
                size_bytes=size_bytes,
                source="PirateBay",
                magnet=magnet,
            )
        )
    return results


# --------------------------------------------------------------------------
# Source: knaben.org (meta-search across TPB, 1337x, Nyaa, YTS, and more)
# --------------------------------------------------------------------------
def search_knaben(query: str) -> List[Result]:
    url = "https://api.knaben.org/v1"
    payload = {
        "search_type": "100%",
        "search_field": "title",
        "query": query,
        "order_by": "seeders",
        "order_direction": "desc",
        "from": 0,
        "size": 50,
        "hide_unsafe": True,
        "hide_xxx": True,
    }
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  [knaben] search failed: {e}", file=sys.stderr)
        return []

    results = []
    for hit in data.get("hits", []):
        name = hit.get("title") or "unknown"
        magnet = hit.get("magnetUrl")
        if not magnet:
            info_hash = hit.get("hash")
            if not info_hash:
                continue  # no way to build a magnet link, skip
            magnet = build_magnet(info_hash, name)
        try:
            seeders = int(hit.get("seeders") or 0)
            leechers = int(hit.get("peers") or 0)
            size_bytes = int(hit.get("bytes") or 0)
        except (TypeError, ValueError):
            continue
        tracker = hit.get("tracker") or "Knaben"
        results.append(
            Result(
                name=name,
                seeders=seeders,
                leechers=leechers,
                size_bytes=size_bytes,
                source=tracker,
                magnet=magnet,
            )
        )
    return results


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
DEFAULT_TRACKERS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
]


def build_magnet(info_hash: str, name: str) -> str:
    params = [("xt", f"urn:btih:{info_hash}"), ("dn", name)]
    magnet = "magnet:?" + urllib.parse.urlencode(params)
    for tr in DEFAULT_TRACKERS:
        magnet += "&tr=" + urllib.parse.quote(tr, safe="")
    return magnet


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"


def dedupe(results: List[Result]) -> List[Result]:
    seen = set()
    unique = []
    for r in results:
        key = re.sub(r"\s+", " ", r.name.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique


def safe_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    return cleaned[:150] or "torrent"


def copy_to_clipboard(text: str) -> bool:
    """Try pyperclip first, then fall back to common OS clipboard utilities."""
    try:
        import pyperclip  # optional dependency

        pyperclip.copy(text)
        return True
    except Exception:
        pass

    candidates = [
        (["pbcopy"], None),                          # macOS
        (["xclip", "-selection", "clipboard"], None),  # Linux (X11)
        (["xsel", "--clipboard", "--input"], None),     # Linux (X11, alt)
        (["wl-copy"], None),                          # Linux (Wayland)
        (["clip.exe"], None),                          # Windows / WSL
    ]
    for cmd, _ in candidates:
        exe = shutil.which(cmd[0])
        if not exe:
            continue
        try:
            subprocess.run(cmd, input=text.encode(), check=True)
            return True
        except Exception:
            continue
    return False


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def run_search(query: str, top_n: int = 15) -> List[Result]:
    print(f"\nSearching for: {query!r}")
    all_results: List[Result] = []
    for label, fn in (("PirateBay (apibay)", search_apibay), ("Knaben (multi-site)", search_knaben)):
        print(f"  querying {label}...")
        all_results.extend(fn(query))

    all_results = dedupe(all_results)
    all_results.sort(key=lambda r: r.seeders, reverse=True)
    return all_results[:top_n]


def print_results(results: List[Result]) -> None:
    if not results:
        print("\nNo results found.")
        return
    print(f"\n{'#':<3} {'S':>5} {'L':>5} {'Size':>9}  {'Source':<12} Name")
    print("-" * 100)
    for i, r in enumerate(results, 1):
        name = r.name if len(r.name) <= 60 else r.name[:57] + "..."
        print(f"{i:<3} {r.seeders:>5} {r.leechers:>5} {human_size(r.size_bytes):>9}  {r.source:<12} {name}")


def handle_selection(r: Result) -> None:
    print(f"\nSelected: {r.name}")
    print(f"Seeders: {r.seeders}  Leechers: {r.leechers}  Size: {human_size(r.size_bytes)}  Source: {r.source}")
    while True:
        print("\nWhat would you like to do?")
        print("  [1] Copy magnet link to clipboard (recommended)")
        print("  [2] Save magnet link as a text file in /magnetfiles")
        print("  [3] Print the magnet link")
        print("  [4] Back to results")
        print("  [q] Quit")
        choice = input("> ").strip().lower()

        if choice == "1":
            if copy_to_clipboard(r.magnet):
                print("Magnet link copied to clipboard.")
                print('Paste it into your torrent client\'s "Add Link" / "Add Magnet Link" '
                      "dialog (NOT \"Add Torrent File\" — that's for real .torrent files).")
            else:
                print("Couldn't find a clipboard tool (tried pyperclip, xclip, xsel, "
                      "wl-copy, pbcopy, clip.exe). Here's the link instead:\n")
                print(r.magnet)
        elif choice == "2":
            os.makedirs(MAGNET_DIR, exist_ok=True)
            filename = safe_filename(r.name) + ".magnet.txt"
            path = os.path.join(MAGNET_DIR, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(r.magnet)
            print(f"Saved to {path}")
            print('NOTE: this is a plain text file containing the magnet link, not a real '
                  '.torrent file. Open it in a text editor and copy the link, then use your '
                  'torrent client\'s "Add Link" / "Add Magnet Link" option — do NOT use '
                  '"Add Torrent File", which expects actual .torrent binary data and will error.')
        elif choice == "3":
            print("\n" + r.magnet)
        elif choice == "4":
            return
        elif choice == "q":
            sys.exit(0)
        else:
            print("Not a valid option.")


def main():
    parser = argparse.ArgumentParser(description="Search multiple torrent sites and rank by seeders.")
    parser.add_argument("query", nargs="?", help="Search term")
    parser.add_argument("-n", "--top", type=int, default=15, help="Number of results to show (default: 15)")
    args = parser.parse_args()

    query = args.query or input("Search term: ").strip()
    if not query:
        print("No search term given.")
        return

    while True:
        results = run_search(query, top_n=args.top)
        print_results(results)

        if not results:
            query = input("\nTry another search term (or press Enter to quit): ").strip()
            if not query:
                return
            continue

        print("\nEnter a result number to select it, 's' to search again, or 'q' to quit.")
        choice = input("> ").strip().lower()

        if choice == "q":
            return
        elif choice == "s":
            query = input("Search term: ").strip()
            if not query:
                return
            continue
        elif choice.isdigit() and 1 <= int(choice) <= len(results):
            handle_selection(results[int(choice) - 1])
        else:
            print("Not a valid choice.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye.")
    except Exception:
        import traceback

        traceback.print_exc()
        # If this was double-clicked on Windows instead of run from a
        # terminal, the window would otherwise close instantly and hide
        # the error above. Keep it open so it can be read/copied.
        if sys.platform == "win32":
            input("\nSomething went wrong (see error above). Press Enter to close...")
        sys.exit(1)
