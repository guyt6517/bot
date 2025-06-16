import os
import shutil
import subprocess
import requests
import tempfile
import winreg

def is_chrome_installed():
    chrome_paths = [
        os.path.join(os.environ['PROGRAMFILES'], 'Google', 'Chrome', 'Application', 'chrome.exe'),
        os.path.join(os.environ['PROGRAMFILES(X86)'], 'Google', 'Chrome', 'Application', 'chrome.exe'),
    ]
    return any(os.path.exists(path) for path in chrome_paths)

def install_chrome():
    print("Downloading Chrome installer...")
    url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    installer_path = os.path.join(tempfile.gettempdir(), "chrome_installer.exe")

    with requests.get(url, stream=True) as r:
        with open(installer_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    print("Running Chrome installer...")
    subprocess.run([installer_path, "/silent", "/install"], check=True)

def is_roblox_installed():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Roblox")
        _ = winreg.QueryValueEx(key, "InstallLocation")
        return True
    except FileNotFoundError:
        return False

def install_roblox():
    print("Downloading Roblox installer...")
    url = "https://setup.rbxcdn.com/RobloxPlayerLauncher.exe"
    installer_path = os.path.join(tempfile.gettempdir(), "roblox_installer.exe")

    with requests.get(url, stream=True) as r:
        with open(installer_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    print("Running Roblox installer...")
    subprocess.run([installer_path], check=True)
