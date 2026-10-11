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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def build_nexus():
    print("=" * 65)
    print("[*] NEXUS MEDIA INGEST — STANDALONE PACKAGING SUITE")
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

    # Pre-clean existing dist/Nexus folder if present
    nexus_dist = os.path.join(dist_dir, "Nexus")
    if os.path.exists(nexus_dist):
        shutil.rmtree(nexus_dist, ignore_errors=True)

    print("[*] Packaging Nexus executable (privacy-safe, no personal cookies or local configs)...")
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--name=Nexus",
        "--noconsole",
        "--clean",
        "--onedir",
        "-y"
    ]

    # Include bin directory if populated
    if os.path.exists(bin_dir) and os.listdir(bin_dir):
        pyinstaller_args.append(f"--add-data={bin_dir};bin")

    pyinstaller_args.extend([
        "--collect-submodules=PyQt6",
        "--collect-submodules=spotdl",
        "--collect-submodules=instaloader",
        "main.py"
    ])

    print(f"[*] Executing command:\n    {' '.join(pyinstaller_args)}\n")
    ret = subprocess.call(pyinstaller_args)

    if ret == 0:
        exe_path = os.path.join(dist_dir, "Nexus", "Nexus.exe")
        nexus_dir = os.path.join(dist_dir, "Nexus")
        zip_output = os.path.join(dist_dir, "Nexus-v1.0.0-Windows-x64")
        
        print("\n[*] Creating GitHub Release ZIP archive...")
        archive_path = shutil.make_archive(zip_output, "zip", dist_dir, "Nexus")
        
        print("\n" + "=" * 65)
        print("✅ BUILD & RELEASE PACKAGING COMPLETED SUCCESSFULLY!")
        print(f"📦 Portable Folder: {nexus_dir}")
        print(f"⚡ Main Executable: {exe_path}")
        print(f"🎁 Release ZIP:     {archive_path}")
        print("=" * 65)
    else:
        print(f"\n❌ Build failed with return code {ret}")
        sys.exit(ret)

if __name__ == "__main__":
    build_nexus()
