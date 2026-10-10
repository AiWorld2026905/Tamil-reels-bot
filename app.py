from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "bot.db"

def setup():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                reel_link TEXT,
                promo_comment TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY,
                clicked_at TEXT
            )
        """)
        if not con.execute("SELECT id FROM settings").fetchone():
            con.execute(
                "INSERT INTO settings (reel_link, promo_comment) VALUES (?, ?)",
                ("", "")
            )

setup()

PAGE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tamil Reels Bot</title>
<style>
body{font-family:Arial;max-width:650px;margin:25px auto;padding:15px;background:#111;color:white}
input,textarea,button{box-sizing:border-box;width:100%;padding:12px;margin:8px 0;border-radius:8px}
input,textarea{background:#222;color:white;border:1px solid #555}
button{background:#27ae60;color:white;border:0;font-size:16px}
.card{background:#222;padding:16px;border-radius:12px;margin:12px 0}
a{color:#8bd5ff}
</style>
</head>
<body>
<h2>🇮🇳 Tamil AI Reels Dashboard</h2>
<div class="card">
<h3>Daily Promotion Settings</h3>
<form method="post" action="/save">
<label>Your Reel link</label>
<input name="link" type="url" placeholder="https://www.instagram.com/reel/..." value="{{link}}" required>
<label>Promotional comment</label>
<textarea name="comment" rows="4" required>{{comment}}</textarea>
<button type="submit">Save Settings</button>
</form>
</div>
<div class="card">
<h3>Link Tracking</h3>
<p>Total tracked clicks: <b>{{clicks}}</b></p>
<a href="/go" target="_blank">Test your tracking link</a>
</div>
<p>Last dashboard load: {{time}}</p>
</body>
</html>
"""

@app.route("/")
def home():
    with sqlite3.connect(DB) as con:
        link, comment = con.execute(
            "SELECT reel_link, promo_comment FROM settings WHERE id=1"
        ).fetchone()
        clicks = con.execute("SELECT COUNT(*) FROM clicks").fetchone()[0]
    return render_template_string(
        PAGE, link=link, comment=comment, clicks=clicks,
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route("/save", methods=["POST"])
def save():
    link = request.form.get("link", "").strip()
    comment = request.form.get("comment", "").strip()
    if not link.startswith("https://www.instagram.com/"):
        return "Please enter a valid Instagram link.", 400
    with sqlite3.connect(DB) as con:
        con.execute(
            "UPDATE settings SET reel_link=?, promo_comment=? WHERE id=1",
            (link, comment)
        )
    return redirect("/")

@app.route("/go")
def go():
    with sqlite3.connect(DB) as con:
        link = con.execute(
            "SELECT reel_link FROM settings WHERE id=1"
        ).fetchone()[0]
        if not link:
            return "Save your Reel link first.", 400
        con.execute(
            "INSERT INTO clicks (clicked_at) VALUES (?)",
            (datetime.now().isoformat(),)
        )
    return redirect(link)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
