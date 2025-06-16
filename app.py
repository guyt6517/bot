from flask import Flask, request, render_template_string
import threading
import time
import psutil
import os
import shutil
import subprocess
import tempfile
import requests
import winreg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# === HTML Web UI ===
form_html = """
<!doctype html>
<title>Roblox Join Bot</title>
<h2>Roblox Auto Joiner</h2>
<form method="POST">
  <label>Username:</label><br>
  <input name="username" required><br><br>
  <label>Password:</label><br>
  <input name="password" type="password" required><br><br>
  <label>Game URL:</label><br>
  <input name="game_url" required><br><br>
  <label>Wait Time (seconds):</label><br>
  <input name="wait_time" value="60"><br><br>
  <label>Number of Cycles:</label><br>
  <input name="cycles" value="3"><br><br>
  <button type="submit">Start Bot</button>
</form>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        game_url = request.form["game_url"]
        wait_time = int(request.form.get("wait_time", 60))
        cycles = int(request.form.get("cycles", 3))

        threading.Thread(target=join_leave_cycle, args=(game_url, username, password, wait_time, cycles)).start()
        return "Bot started! You can close this tab."

    return render_template_string(form_html)

# === Roblox + Chrome Dependency Checks ===
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
        _, _ = winreg.QueryValueEx(key, "InstallLocation")
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

# === Core Logic ===
def kill_roblox():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'RobloxPlayerBeta' in proc.info['name']:
            print(f"Killing Roblox process: {proc.info['name']} (PID {proc.info['pid']})")
            psutil.Process(proc.info['pid']).kill()

def roblox_login(driver, username, password):
    driver.get("https://www.roblox.com/login")
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "login-username")))
    driver.find_element(By.ID, "login-username").send_keys(username)
    driver.find_element(By.ID, "login-password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()
    WebDriverWait(driver, 15).until(EC.url_contains("roblox.com/home"))
    print("Logged in.")

def join_game(driver, game_url):
    driver.get(game_url)
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Play')]"))
    ).click()
    print("Clicked Play — Roblox should launch.")

def join_leave_cycle(game_url, username, password, wait_seconds=60, cycles=3):
    # Auto-install requirements
    if not is_chrome_installed():
        install_chrome()
    if not is_roblox_installed():
        install_roblox()

    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--window-position=0,1000")  # Minimized
    chrome_options.add_argument("--start-maximized")
    service = Service("chromedriver")  # Ensure chromedriver.exe is in the same dir or PATH

    driver = webdriver.Chrome(service=service, options=chrome_options)

    roblox_login(driver, username, password)

    for i in range(cycles):
        print(f"Cycle {i + 1}/{cycles}")
        join_game(driver, game_url)
        time.sleep(wait_seconds)
        kill_roblox()
        time.sleep(5)

    driver.quit()
