#!/usr/bin/env python3
"""
dev_setup.py

OPTIONAL: sets up a local dev environment to run torrent_search.py directly
from source, without building the .exe. Useful on macOS/Linux, or for
testing changes quickly. Windows users who just want the app should use
build_exe.bat + install.ps1 instead (see README.md).

Everything this creates stays inside this project folder — nothing is
installed system-wide or to your user site-packages:

  - ./venv/               a local virtual environment
  - ./magnetfiles/         where saved magnet links go
  - ./run.bat / ./run.sh   convenience launchers that use the local venv

This script deletes itself once setup finishes successfully — it's meant
to be run exactly once.

Usage:
    python dev_setup.py
"""

import os
import subprocess
import sys
import venv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
VENV_DIR = os.path.join(ROOT_DIR, "venv")
MAGNET_DIR = os.path.join(ROOT_DIR, "magnetfiles")
REQUIREMENTS = os.path.join(SRC_DIR, "requirements.txt")
MAIN_SCRIPT = os.path.join(SRC_DIR, "torrent_search.py")


def venv_python() -> str:
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def create_venv():
    if os.path.exists(venv_python()):
        print(f"Virtual environment already exists at {VENV_DIR}, reusing it.")
        return
    print(f"Creating local virtual environment at {VENV_DIR} ...")
    venv.EnvBuilder(with_pip=True).create(VENV_DIR)


def install_requirements():
    if not os.path.exists(REQUIREMENTS):
        print(f"Warning: {REQUIREMENTS} not found, skipping dependency install.")
        return
    print("Installing dependencies into the local venv...")
    subprocess.run([venv_python(), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([venv_python(), "-m", "pip", "install", "-r", REQUIREMENTS], check=True)


def create_magnet_dir():
    os.makedirs(MAGNET_DIR, exist_ok=True)
    print(f"Magnet files will be saved to {MAGNET_DIR}")


def write_launchers():
    bat_path = os.path.join(ROOT_DIR, "run.bat")
    with open(bat_path, "w") as f:
        f.write(
            "@echo off\r\n"
            'cd /d "%~dp0"\r\n'
            'set "TORRENT_SEARCH_MAGNET_DIR=%~dp0magnetfiles"\r\n'
            'venv\\Scripts\\python.exe src\\torrent_search.py %*\r\n'
            "pause\r\n"
        )

    sh_path = os.path.join(ROOT_DIR, "run.sh")
    with open(sh_path, "w") as f:
        f.write(
            "#!/usr/bin/env bash\n"
            'cd "$(dirname "$0")"\n'
            'export TORRENT_SEARCH_MAGNET_DIR="$(pwd)/magnetfiles"\n'
            './venv/bin/python src/torrent_search.py "$@"\n'
        )
    try:
        os.chmod(sh_path, 0o755)
    except OSError:
        pass

    print(f"Created {bat_path} and {sh_path}")


def delete_self():
    """Remove this installer once setup is done - it's a one-time-use script."""
    try:
        os.remove(os.path.abspath(__file__))
        print("\nRemoved dev_setup.py (one-time setup, no longer needed).")
    except OSError as e:
        print(f"\nCould not remove dev_setup.py automatically ({e}). "
              "You can safely delete it yourself now.")


def main():
    if not os.path.exists(MAIN_SCRIPT):
        print(f"Error: expected to find {MAIN_SCRIPT} but it's missing.", file=sys.stderr)
        sys.exit(1)

    print(f"Setting up torrent-search (dev/source mode) in: {ROOT_DIR}\n")
    create_venv()
    install_requirements()
    create_magnet_dir()
    write_launchers()

    print("\nSetup complete.")
    if sys.platform == "win32":
        print('Run it with:  run.bat "your search term"')
        print('(or:  venv\\Scripts\\python.exe src\\torrent_search.py "your search term")')
    else:
        print('Run it with:  ./run.sh "your search term"')
        print('(or:  ./venv/bin/python src/torrent_search.py "your search term")')

    delete_self()


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\nSetup failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        import traceback

        traceback.print_exc()
        if sys.platform == "win32":
            input("\nSomething went wrong (see error above). Press Enter to close...")
        sys.exit(1)
