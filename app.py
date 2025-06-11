from flask import Flask, render_template, request, redirect, session
import random, json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'color-game-secret'

USERS_FILE = "users.json"
RESULTS_FILE = "results.json"

def load_data(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
    with open(filename, "r") as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def get_user(username):
    users = load_data(USERS_FILE)
    if username not in users:
        users[username] = {"balance": 50, "ref": None, "bonus_claimed": False}
        save_data(USERS_FILE, users)
    return users[username]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        session["username"] = username
        get_user(username)
        return redirect("/dashboard")
    return render_template("index.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    username = session.get("username")
    if not username:
        return redirect("/")
    user = get_user(username)
    results = load_data(RESULTS_FILE)
    last_result = results.get("last_result", "None")
    return render_template("dashboard.html", user=user, last_result=last_result)

@app.route("/predict", methods=["POST"])
def predict():
    username = session.get("username")
    if not username:
        return redirect("/")
    color = request.form.get("color")
    user = get_user(username)

    result = random.choice(["Red", "Green", "Violet"])
    win = (color == result)
    if win:
        user["balance"] += 10
    else:
        user["balance"] -= 5

    users = load_data(USERS_FILE)
    users[username] = user
    save_data(USERS_FILE, users)

    results = {"last_result": result, "time": datetime.now().isoformat()}
    save_data(RESULTS_FILE, results)

    return redirect("/dashboard")

@app.route("/bonus")
def bonus():
    username = session.get("username")
    if not username:
        return redirect("/")
    user = get_user(username)
    if not user["bonus_claimed"]:
        user["balance"] += 5
        user["bonus_claimed"] = True
        users = load_data(USERS_FILE)
        users[username] = user
        save_data(USERS_FILE, users)
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)