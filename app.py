import sqlite3
import pyperclip
import time
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify, request

DB_NAME = "neurodesk.db"
app = Flask(__name__)

# ---------- GLOBAL STATE ----------
listening = True  # controls whether clipboard listener is active


# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clipboard_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            is_favourite INTEGER DEFAULT 0,
            is_pinned INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ---------- DATABASE OPERATIONS ----------
def insert_clipboard(content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clipboard_history (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()


def toggle_favourite(entry_id, status: bool = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if status is None:
        cursor.execute("SELECT is_favourite FROM clipboard_history WHERE id=?", (entry_id,))
        row = cursor.fetchone()
        status = not bool(row[0]) if row else True

    cursor.execute("UPDATE clipboard_history SET is_favourite=? WHERE id=?", (1 if status else 0, entry_id))
    conn.commit()
    conn.close()


def toggle_pinned(entry_id, status: bool = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if status is None:
        cursor.execute("SELECT is_pinned FROM clipboard_history WHERE id=?", (entry_id,))
        row = cursor.fetchone()
        status = not bool(row[0]) if row else True

    cursor.execute("UPDATE clipboard_history SET is_pinned=? WHERE id=?", (1 if status else 0, entry_id))
    conn.commit()
    conn.close()


def get_all_entries():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, is_favourite, is_pinned, timestamp
        FROM clipboard_history
        ORDER BY 
            is_pinned DESC,
            timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------- CLIPBOARD LISTENER ----------
def listen_clipboard(interval=1):
    global listening
    print("📋 NeuroDesk Clipboard Listener Started...")
    last_text = ""

    while True:
        try:
            if listening:  # only record when not paused
                text = pyperclip.paste()
                if text and text != last_text:
                    insert_clipboard(text)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Saved: {text[:60]}...")
                    last_text = text
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Stopped listening.")
            break


# ---------- FLASK API ----------
@app.route("/history", methods=["GET"])
def api_get_history():
    rows = get_all_entries()
    data = [
        {
            "id": r[0],
            "content": r[1],
            "is_favourite": bool(r[2]),
            "is_pinned": bool(r[3]),
            "timestamp": r[4]
        }
        for r in rows
    ]
    return jsonify(data)


@app.route("/favourite/<int:entry_id>", methods=["POST"])
def api_toggle_favourite(entry_id):
    status = request.json.get("status") if request.is_json else None
    toggle_favourite(entry_id, status)
    return jsonify({"success": True})


@app.route("/pin/<int:entry_id>", methods=["POST"])
def api_toggle_pin(entry_id):
    status = request.json.get("status") if request.is_json else None
    toggle_pinned(entry_id, status)
    return jsonify({"success": True})


@app.route("/delete/<int:entry_id>", methods=["DELETE"])
def api_delete_entry(entry_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clipboard_history WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/clear", methods=["DELETE"])
def api_clear_all():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clipboard_history")
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/pause", methods=["POST"])
def api_pause():
    global listening
    listening = False
    print("⏸ Clipboard listening paused.")
    return jsonify({"success": True, "listening": listening})


@app.route("/resume", methods=["POST"])
def api_resume():
    global listening
    listening = True
    print("▶ Clipboard listening resumed.")
    return jsonify({"success": True, "listening": listening})


# ---------- MAIN ----------
if __name__ == "__main__":
    init_db()

    # Run clipboard listener in background
    listener_thread = Thread(target=listen_clipboard, daemon=True)
    listener_thread.start()

    # Start Flask API
    app.run(host="127.0.0.1", port=5000, debug=False)
