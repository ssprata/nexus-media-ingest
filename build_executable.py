"""
Nexus Standalone Executable Packaging Suite
Generates a portable, standalone Windows executable distribution of Nexus.
Usage:
    python build_executable.py
"""

import os
import sys
import subprocess
import shutil

def build_nexus():
    print("=" * 65)
    print("🚀 NEXUS MEDIA INGEST — STANDALONE PACKAGING SUITE")
    print("=" * 65)

    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(workspace_dir)

    # 1. Ensure PyInstaller is installed
    try:
        import PyInstaller
        print(f"[*] PyInstaller detected: v{PyInstaller.__version__}")
    except ImportError:
        print("[*] PyInstaller not detected. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Check binary directory
    bin_dir = os.path.join(workspace_dir, "bin")
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir, exist_ok=True)
    print(f"[*] Core engine binary directory: {bin_dir}")

    # 3. Assemble PyInstaller arguments
    dist_dir = os.path.join(workspace_dir, "dist")
    build_dir = os.path.join(workspace_dir, "build")

    print("[*] Packaging Nexus executable...")
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--name=Nexus",
        "--noconsole",
        "--clean",
        "--onedir",
        f"--add-data={bin_dir};bin",
        f"--add-data={os.path.join(workspace_dir, 'config.json')};.",
        f"--add-data={os.path.join(workspace_dir, 'cookies.txt')};.",
        "--collect-submodules=PyQt6",
        "--collect-submodules=spotdl",
        "--collect-submodules=instaloader",
        "main.py"
    ]

    print(f"[*] Executing command:\n    {' '.join(pyinstaller_args)}\n")
    ret = subprocess.call(pyinstaller_args)

    if ret == 0:
        exe_path = os.path.join(dist_dir, "Nexus", "Nexus.exe")
        print("\n" + "=" * 65)
        print("✅ BUILD COMPLETED SUCCESSFULLY!")
        print(f"📦 Portable Distribution: {os.path.join(dist_dir, 'Nexus')}")
        print(f"⚡ Main Executable: {exe_path}")
        print("=" * 65)
    else:
        print(f"\n❌ Build failed with return code {ret}")
        sys.exit(ret)

if __name__ == "__main__":
    build_nexus()
