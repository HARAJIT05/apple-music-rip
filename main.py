import os
import subprocess
import sys
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
WRAPPER_DIR = PROJECT_DIR / "wrapper"
AMD_DIR = PROJECT_DIR / "apple-music-downloader"

def is_nix_installed():
    if shutil.which("nix-shell"):
        return True
    # Check common locat=ions
    candidates = [
        "/nix/var/nix/profiles/default/bin/nix-shell",
        os.path.expanduser("~/.nix-profile/bin/nix-shell"),
        "/run/current-system/sw/bin/nix-shell"
    ]
    for c in candidates:
        if os.path.exists(c):
            return True
    return False

def install_nix():
    print("⬇️ Nix not found. Installing Nix...")
    try:
        # Use the official installer
        # We avoid process substitution <(...) because sh might not support it
        download_cmd = "curl -L https://nixos.org/nix/install -o install-nix.sh"
        subprocess.run(download_cmd, shell=True, check=True)

        install_cmd = "sh install-nix.sh --no-daemon --yes"
        
        # If not root, we might need to use non-daemon or let the script handle sudo
        if os.geteuid() != 0:
             print("ℹ️ Running as non-root, attempting Nix installation (sudo might be required)...")
             # The script will prompt for sudo if needed for daemon install, or we can use --no-daemon
             install_cmd = "sh install-nix.sh --no-daemon --yes"
        
        subprocess.run(install_cmd, shell=True, check=True)
        print("✅ Nix installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Nix: {e}")
        print("Please install Nix manually: https://nixos.org/download.html")
        sys.exit(1)
    finally:
        if os.path.exists("install-nix.sh"):
            os.remove("install-nix.sh")

def ensure_nix_environment():
    # Check if we are already running inside the Nix shell wrapper
    if os.environ.get("GEMINI_WRAPPED") == "1":
        return

    if not is_nix_installed():
        install_nix()
    
    print("🔄 Switching to Nix environment...")
    
    nix_shell_cmd = shutil.which("nix-shell")
    if not nix_shell_cmd:
        # Try to find it in common paths if not in PATH yet
        candidates = [
            "/nix/var/nix/profiles/default/bin/nix-shell",
            os.path.expanduser("~/.nix-profile/bin/nix-shell"),
            "/run/current-system/sw/bin/nix-shell"
        ]
        for c in candidates:
            if os.path.exists(c):
                nix_shell_cmd = c
                break
    
    if not nix_shell_cmd:
        # If we just installed Nix, we might need to source the profile
        # But we can't easily source in python.
        # We can try to guess the path or ask user to restart shell.
        print("⚠️ Could not find nix-shell in PATH. If you just installed Nix, you might need to restart your shell.")
        # Try absolute path for standard multi-user install
        if os.path.exists("/nix/var/nix/profiles/default/bin/nix-shell"):
             nix_shell_cmd = "/nix/var/nix/profiles/default/bin/nix-shell"
        else:
             sys.exit(1)

    # Relaunch inside nix-shell
    shell_file = PROJECT_DIR / "shell.nix"
    script_file = PROJECT_DIR / "main.py"
    
    # Propagate args
    args = sys.argv[1:]
    
    # We use execv to replace the process
    cmd = [
        nix_shell_cmd, 
        str(shell_file), 
        "--run", 
        f"python3 {script_file} {' '.join(args)}"
    ]
    
    try:
        print(f"Running: {' '.join(cmd)}")
        os.execv(nix_shell_cmd, cmd)
    except OSError as e:
        print(f"❌ Failed to execute nix-shell: {e}")
        sys.exit(1)

def setup_wrapper():
    # Clone and compile wrapper if not exists
    if (WRAPPER_DIR / "wrapper").exists() and (WRAPPER_DIR / "rootfs").exists():
        print("ℹ️ Wrapper already exists, skipping setup")
        return

    WRAPPER_REPO = "https://github.com/WorldObservationLog/wrapper.git"
    temp_dir = PROJECT_DIR / "wrapper_temp"
    deps_dir = PROJECT_DIR / "deps"
    ndk_dir = deps_dir / "android-ndk-r23b"

    # Clean up temp dir if it exists from a previous failed run
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # 1. Setup NDK
    if not ndk_dir.exists():
        print("⬇️ Android NDK not found. Downloading...")
        deps_dir.mkdir(parents=True, exist_ok=True)
        ndk_zip = deps_dir / "android-ndk-r23b-linux.zip"
        try:
            subprocess.run(
                ["wget", "-O", str(ndk_zip), "https://dl.google.com/android/repository/android-ndk-r23b-linux.zip"],
                check=True
            )
            print("📦 Unzipping NDK...")
            subprocess.run(["unzip", "-q", "-d", str(deps_dir), str(ndk_zip)], check=True)
            # Remove zip to save space? Optional.
            if ndk_zip.exists():
                os.remove(ndk_zip)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup NDK: {e}")
            sys.exit(1)
    
    print(f"⬇️ Cloning wrapper from {WRAPPER_REPO}...")
    try:
        subprocess.run(["git", "clone", WRAPPER_REPO, str(temp_dir)], check=True)
        
        build_dir = temp_dir / "build"
        build_dir.mkdir()
        
        print("⚙️ Compiling wrapper...")
        # We need to set HOME to deps_dir because CMakeLists.txt expects NDK at $HOME/android-ndk-r23b
        env = os.environ.copy()
        env["HOME"] = str(deps_dir)
        
        subprocess.run(["cmake", ".."], cwd=build_dir, env=env, check=True)
        # Get core count for parallel build
        nproc = subprocess.check_output(["nproc"]).decode().strip()
        subprocess.run(["make", f"-j{nproc}"], cwd=build_dir, env=env, check=True)
        
        WRAPPER_DIR.mkdir(parents=True, exist_ok=True)
        
        # Copy wrapper binary
        # The wrapper binary is built in the source directory (temp_dir) due to BUILD_IN_SOURCE 1
        if (temp_dir / "wrapper").exists():
            shutil.move(str(temp_dir / "wrapper"), str(WRAPPER_DIR / "wrapper"))
        else:
            # Fallback or check if it's in build_dir just in case, though logs show otherwise
            print(f"⚠️ Could not find wrapper binary in {temp_dir / 'wrapper'}")
            shutil.move(str(build_dir / "wrapper"), str(WRAPPER_DIR / "wrapper"))
        
        # Copy rootfs
        # If rootfs already exists in destination, remove it first?
        if (WRAPPER_DIR / "rootfs").exists():
            shutil.rmtree(WRAPPER_DIR / "rootfs")
        shutil.copytree(str(temp_dir / "rootfs"), str(WRAPPER_DIR / "rootfs"))

        # Cleanup temp
        shutil.rmtree(temp_dir)
        print("✅ Wrapper setup complete")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup wrapper: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        sys.exit(1)

def clone_amd_repo():
    if AMD_DIR.exists():
        print("ℹ️ Apple Music Downloader already exists, skipping clone")
        return

    print("⬇️ Cloning Apple Music Downloader...")
    try:
        subprocess.run(
            ["git", "clone", "https://github.com/zhaarey/apple-music-downloader", str(AMD_DIR)],
            check=True
        )
        print("✅ Apple Music Downloader cloned inside project folder")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone Apple Music Downloader: {e}")
        sys.exit(1)

def start():
    print("🚀 Starting Apple Music Downloader Web UI...")
    
    # Add Wrapper to PATH
    os.environ["PATH"] = f"{WRAPPER_DIR}:{os.environ['PATH']}"
    
    # Set executable permissions for the wrapper
    wrapper_path = WRAPPER_DIR / "wrapper"
    if wrapper_path.exists():
        wrapper_path.chmod(0o755)

    # Import and run the Flask app
    try:
        from app import app
        app.run(host="0.0.0.0", port=5000, debug=True)
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("Ensure you are running inside the nix-shell environment.")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure we are in Nix environment
    ensure_nix_environment()
    
    # Dependencies are now met (via nix-shell)
    setup_wrapper()
    clone_amd_repo()
    
    start()