import sys
import subprocess
import importlib

REQUIRED = [
    ("PyQt6.QtWidgets",  "PyQt6"),
    ("PyQt6.QtMultimedia", "PyQt6"),
    ("qframelesswindow", "PyQt6-Frameless-Window"),
    ("msoc",             "msoc"),
    ("requests",         "requests"),
    ("bs4",              "beautifulsoup4"),
    ("lxml",             "lxml"),
    ("aiohttp",          "aiohttp"),
]


def is_installed(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def install_package(pip_name: str) -> bool:
    print(f"  -> Installing {pip_name}...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pip_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        return True
    except subprocess.CalledProcessError:
        print(f"  x Failed to install {pip_name}")
        return False


def ensure_dependencies():
    print("=" * 50)
    print("  Checking dependencies...")
    print("=" * 50)

    missing = []
    for module_name, pip_name in REQUIRED:
        if is_installed(module_name):
            print(f"  [OK] {pip_name}")
        else:
            print(f"  [MISSING] {pip_name}")
            missing.append(pip_name)

    if not missing:
        print("\n[OK] All dependencies are installed.\n")
        return True

    print(f"\n[!] Missing {len(missing)} package(s). Installing...\n")

    failed = []
    for pip_name in missing:
        if not install_package(pip_name):
            failed.append(pip_name)

    if failed:
        print("\n[ERROR] Failed to install:")
        for f in failed:
            print(f"  - {f}")
        return False

    print("\n[OK] All dependencies installed. Restart the player.\n")
    return True


if __name__ == "__main__":
    ensure_dependencies()