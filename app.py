from flask import Flask
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

# === CONFIGURE YOUR SETTINGS HERE ===
USERNAME = "hgfrytfgjftyyjgh"
PASSWORD = "bm3047854"
GAME_URL = "https://www.roblox.com/games/1234567890/Your-Game"
WAIT_SECONDS = 60
CYCLES = 3
# =====================================

app = Flask(__name__)

@app.route("/")
def index():
    return "Roblox bot is running."

# === Installer Functions ===
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

# === Roblox Automation ===
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
    if not is_chrome_installed():
        install_chrome()
    if not is_roblox_installed():
        install_roblox()

    chrome_options = Options()
    chrome_options.add_argument("--window-position=0,1000")  # Simulates minimized window
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service("chromedriver"), options=chrome_options)

    try:
        roblox_login(driver, username, password)

        for i in range(cycles):
            print(f"Cycle {i + 1}/{cycles}")
            join_game(driver, game_url)
            time.sleep(wait_seconds)
            kill_roblox()
            time.sleep(5)
    finally:
        driver.quit()

# === Background Task: Runs Once on Startup ===
def start_bot_thread():
    threading.Thread(target=join_leave_cycle, args=(GAME_URL, USERNAME, PASSWORD, WAIT_SECONDS, CYCLES)).start()

start_bot_thread()
