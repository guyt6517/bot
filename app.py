import os
import shutil
import tempfile
import threading
import time
import requests
import subprocess
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIG ===
USERNAME = "hgfrytfgjftyyjgh"
PASSWORD = "bm3047854"
GAME_URL = "https://www.roblox.com/games/96666062715851/Public-Bathroom-Simulator"
WAIT_SECONDS = 60
CYCLES = 3

app = Flask(__name__)

def is_command_available(cmd):
    return shutil.which(cmd) is not None

def install_chrome():
    print("Attempting to install Chromium via apt...")
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "chromium-browser"], check=True)

def is_chrome_installed():
    return is_command_available("google-chrome") or is_command_available("chromium-browser")

def is_sober_installed():
    return is_command_available("sober")

def install_sober():
    sober_url = "https://github.com/soberwp/sober/releases/latest/download/sober-linux-x64"
    target_path = "/usr/local/bin/sober"
    tmp_path = os.path.join(tempfile.gettempdir(), "sober-linux-x64")

    print(f"Downloading Sober from {sober_url} ...")
    with requests.get(sober_url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    print("Download complete. Installing... (requires sudo)")
    subprocess.run(["sudo", "mv", tmp_path, target_path], check=True)
    subprocess.run(["sudo", "chmod", "+x", target_path], check=True)
    print(f"Sober installed to {target_path}")

def kill_roblox():
    # Kill sober or wine Roblox process if running
    proc_list = subprocess.check_output(["ps", "ax"]).decode().splitlines()
    for proc in proc_list:
        if "sober" in proc or "RobloxPlayerBeta" in proc:
            pid = int(proc.strip().split()[0])
            print(f"Killing process {pid} for Roblox")
            subprocess.run(["kill", "-9", str(pid)])

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
    if not is_sober_installed():
        install_sober()

    chrome_options = Options()
    chrome_path = shutil.which("google-chrome") or shutil.which("chromium-browser")
    if chrome_path:
        chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--window-position=0,1000")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")  # comment out if want visible browser

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

def start_bot_thread():
    threading.Thread(target=join_leave_cycle, args=(GAME_URL, USERNAME, PASSWORD, WAIT_SECONDS, CYCLES), daemon=True).start()

@app.route("/")
def index():
    return jsonify({"status": "Roblox bot is running."})

@app.route("/start")
def start_bot():
    start_bot_thread()
    return jsonify({"status": "Bot started"})

if __name__ == "__main__":
    start_bot_thread()
    app.run(host="0.0.0.0", port=8000)
