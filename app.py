from installer_utils import is_chrome_installed, install_chrome, is_roblox_installed, install_roblox
# app.py
from flask import Flask, request, render_template_string
import threading
import time
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

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

def kill_roblox():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'RobloxPlayerBeta' in proc.info['name']:
            psutil.Process(proc.info['pid']).kill()

def roblox_login(driver, username, password):
    driver.get("https://www.roblox.com/login")
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "login-username")))
    driver.find_element(By.ID, "login-username").send_keys(username)
    driver.find_element(By.ID, "login-password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()
    WebDriverWait(driver, 15).until(EC.url_contains("roblox.com/home"))

def join_game(driver, game_url):
    driver.get(game_url)
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Play')]"))
    ).click()

def join_leave_cycle(game_url, username, password, wait_seconds=60, cycles=3):
    chrome_options = Options()
    chrome_options.add_argument("--window-position=0,1000")  # Minimized
    chrome_options.add_argument("--start-maximized")
    service = Service("chromedriver")  # Ensure chromedriver is in the PATH or same directory

    driver = webdriver.Chrome(service=service, options=chrome_options)
    roblox_login(driver, username, password)

    for i in range(cycles):
        join_game(driver, game_url)
        time.sleep(wait_seconds)
        kill_roblox()
        time.sleep(5)

    driver.quit()
