import threading
import time
import datetime
import requests
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# ===== CONFIGURATION =====
TELEGRAM_BOT_TOKEN = "8608137401:AAHeqrVewTaeMaq_YbnKGRw_07MFtQ3qjdc"
CHANNEL_ID = "-1003775121108"
GAME_NAME = "TARGET KING"
CHANNEL_LINK = "https://t.me/+mIkGfeLObEoxZTA9"
GAME_URL = "https://www.khelv.info/#/register?invitationCode=91571239301"

# Official Live Wingo API Endpoint (Globally Defined)
WINGO_API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?pageSize=10&pageNo=1"

# Sticker IDs
WIN_STICKER_ID = ""  
LOSS_STICKER_ID = "" 

# Stats Counters for Wins and Losses
stats_counter = {
    "wins": 0,
    "losses": 0
}

# Clean Global State
latest_data = {
    "period": "",
    "time_remaining": 60,
    "predicted_number": 0,
    "result_type": "BIG",
    "level": 1,
    "history": []
}

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TIGER PRIME HACKER • ELITE</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; user-select: none; -webkit-tap-highlight-color: transparent; }
        body { background: #020104; font-family: 'Plus Jakarta Sans', sans-serif; color: #f3e8ff; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 10px; overflow: hidden; position: relative; }
        body::before { content: ''; position: absolute; top: -30%; left: -30%; width: 160%; height: 160%; background: radial-gradient(circle at 50% 20%, rgba(255, 119, 0, 0.15) 0%, transparent 45%), radial-gradient(circle at 80% 80%, rgba(255, 41, 117, 0.18) 0%, transparent 55%), radial-gradient(circle at 20% 70%, rgba(147, 51, 234, 0.22) 0%, transparent 50%); animation: ambientShift 12s ease infinite alternate; pointer-events: none; }
        @keyframes ambientShift { 0% { transform: scale(1); opacity: 0.8; } 100% { transform: scale(1.08); opacity: 1; } }
        #ui { display: flex; width: 100%; max-width: 420px; flex-direction: column; height: 97vh; background: linear-gradient(145deg, rgba(18, 8, 32, 0.96) 0%, rgba(3, 1, 6, 0.99) 100%); backdrop-filter: blur(40px); border-radius: 36px; border: 2px solid rgba(255, 119, 0, 0.5); padding: 18px 14px 14px 14px; box-shadow: 0 35px 80px rgba(0, 0, 0, 0.95), 0 0 60px rgba(255, 119, 0, 0.2) inset, 0 0 35px rgba(255, 41, 117, 0.25); position: relative; overflow: hidden; }
        .pages-container { flex-grow: 1; overflow-y: auto; scrollbar-width: thin; padding-bottom: 8px; }
        .pages-container::-webkit-scrollbar { width: 3px; }
        .pages-container::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #ff7700, #ff2975); border-radius: 20px; }
        .page { display: none; flex-direction: column; height: 100%; animation: fadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1); }
        .page.active { display: flex; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px) scale(0.99); } to { opacity: 1; transform: translateY(0) scale(1); } }
        .logo-box { text-align: center; margin-bottom: 14px; position: relative; }
        .logo { font-family: 'Orbitron', sans-serif; font-size: 23px; font-weight: 900; background: linear-gradient(135deg, #fff 15%, #ff7700 50%, #ff2975 100%); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: 2px; text-shadow: 0 4px 25px rgba(255, 119, 0, 0.5); text-transform: uppercase; }
        .badge-prime { display: inline-block; background: linear-gradient(90deg, #ff7700, #ffaa00, #ff2975); background-size: 200% auto; animation: gradientMove 4s linear infinite; color: #030107; font-size: 9px; font-weight: 900; padding: 3px 12px; border-radius: 12px; letter-spacing: 2px; margin-top: 5px; text-transform: uppercase; box-shadow: 0 0 15px rgba(255, 119, 0, 0.6); }
        @keyframes gradientMove { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
        .action-btn { width: 100%; padding: 10px; border-radius: 12px; font-weight: 800; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; cursor: pointer; border: none; transition: 0.2s; margin-bottom: 6px; }
        .btn-win { background: rgba(16, 185, 129, 0.3); color: #34d399; border: 1px solid #10b981; }
        .period-card { background: linear-gradient(135deg, rgba(45, 20, 75, 0.85) 0%, rgba(12, 5, 25, 0.95) 100%); padding: 14px 18px; border-radius: 22px; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255, 119, 0, 0.4); margin-bottom: 10px; }
        .p-label { font-size: 10px; color: #ffaa00; font-weight: 800; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 3px; }
        .p-val { font-size: 20px; font-family: 'Orbitron', sans-serif; font-weight: 700; color: #fff; }
        .timer-val { font-size: 24px; font-weight: 900; color: #ff2975; font-family: 'Orbitron', monospace; background: rgba(255, 41, 117, 0.12); padding: 6px 14px; border-radius: 12px; border: 1.5px solid rgba(255, 41, 117, 0.5); }
        .pred-card { background: linear-gradient(145deg, #1c0b38 0%, #05020c 100%); border-radius: 24px; flex-grow: 1; min-height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 2px solid rgba(255, 119, 0, 0.5); margin-bottom: 10px; position: relative; overflow: hidden; }
        .res-text { font-family: 'Orbitron', sans-serif; font-size: 42px; font-weight: 900; background: linear-gradient(135deg, #ffaa00 0%, #ff2975 100%); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 4px; }
        .level-tag { font-family: 'Orbitron', sans-serif; font-size: 11px; color: #ffaa00; background: rgba(255,170,0,0.15); padding: 3px 10px; border-radius: 8px; border: 1px solid #ffaa00; margin-bottom: 6px; }
        .num-container { display: flex; gap: 22px; margin-top: 5px; }
        .num-ball { width: 60px; height: 60px; background: radial-gradient(circle at 35% 35%, #5a2590, #140529); border: 3px solid #ffaa00; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-family: 'Orbitron', sans-serif; font-size: 28px; font-weight: 900; color: #ffaa00; }
        .session-box { flex-grow: 1; background: rgba(10, 4, 20, 0.92); border-radius: 20px; padding: 8px; border: 1.5px solid rgba(255, 119, 0, 0.3); overflow-y: auto; max-height: calc(100vh - 160px); }
        table { width: 100%; border-collapse: collapse; }
        td { padding: 10px 6px; text-align: center; font-size: 12px; border-bottom: 1px solid rgba(147, 51, 234, 0.25); color: #e9d5ff; }
        th { color: #ffaa00; font-size: 10px; padding: 7px 0; text-transform: uppercase; font-weight: 700; background: rgba(255, 119, 0, 0.08); border-radius: 8px; }
        .tag-win { background: rgba(16, 185, 129, 0.22); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.6); padding: 4px 10px; border-radius: 12px; font-size: 9px; font-weight: 900; }
        .tag-loss { background: rgba(239, 68, 68, 0.22); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.6); padding: 4px 10px; border-radius: 12px; font-size: 9px; font-weight: 800; }
        .bottom-nav { display: flex; justify-content: space-around; background: rgba(10, 4, 20, 0.96); padding: 8px 6px; border-radius: 18px; border: 1.5px solid rgba(255, 119, 0, 0.4); margin-top: 8px; }
        .nav-item { background: transparent; border: none; color: #a855f7; font-size: 11px; font-weight: 800; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; padding: 6px 14px; border-radius: 12px; }
        .nav-item svg { width: 19px; height: 19px; fill: currentColor; }
        .nav-item.active { background: linear-gradient(135deg, rgba(255, 119, 0, 0.3), rgba(255, 41, 117, 0.4)); color: #ffaa00; border: 1px solid rgba(255, 119, 0, 0.7); }
    </style>
</head>
<body>

<div class="container" id="ui">
    <div class="logo-box">
        <div class="logo">⚡ TIGER LEGACY ⚡</div>
        <div class="badge-prime" id="badgeMode">Elite Hacker Edition</div>
    </div>
    
    <div class="pages-container">
        <!-- PAGE 1: PREDICTION -->
        <div id="page-prediction" class="page active">
            <div class="period-card">
                <div>
                    <div class="p-label">Target Period</div>
                    <div class="p-val" id="nextP">----</div>
                </div>
                <div>
                    <div class="p-label" style="text-align: right;">AI Countdown</div>
                    <div class="timer-val" id="timer">00:00</div>
                </div>
            </div>
            
            <div class="pred-card">
                <div class="level-tag" id="lvlTag">LEVEL 1</div>
                <div id="res" class="res-text">SCAN</div>
                <div class="num-container">
                    <div class="num-ball" id="n1">?</div>
                </div>
            </div>
        </div>

        <!-- PAGE 2: HISTORY -->
        <div id="page-history" class="page">
            <div class="session-box">
                <table>
                    <thead>
                        <tr>
                            <th>📆 PERIOD</th>
                            <th>🎲 NUM</th>
                            <th>📏 STATUS</th>
                        </tr>
                    </thead>
                    <tbody id="session-h"></tbody>
                </table>
            </div>
        </div>

        <!-- PAGE 3: WEB VIEW -->
        <div id="page-webview" class="page">
            <div class="webview-box" style="display:flex; flex-direction:column; height:100%; gap:8px;">
                <div class="url-bar-container" style="display:flex; gap:8px;">
                    <input type="text" id="urlInput" class="form-input" placeholder="Enter target URL" style="margin:0;">
                    <button class="action-btn btn-win" onclick="loadWebsite()" style="width:auto; padding:0 14px; margin:0;">EXECUTE</button>
                </div>
                <div class="iframe-wrapper" style="flex-grow:1; background:#fff; border-radius:18px; overflow:hidden; border:2px solid rgba(255,119,0,0.5); position:relative;">
                    <div id="iframePlaceholder" style="position:absolute; top:0; left:0; width:100%; height:100%; display:flex; justify-content:center; align-items:center; background:#0b0315; color:#ffaa00; font-weight:800; font-size:12px; text-align:center; padding:20px;">Enter link above and click EXECUTE to load platform</div>
                    <iframe id="webFrame" style="width:100%; height:100%; border:none;" src=""></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- BOTTOM NAVIGATION -->
    <div class="bottom-nav" id="bottomNav">
        <button class="nav-item active" onclick="switchPage('prediction', this)">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
            Hacker
        </button>
        <button class="nav-item" onclick="switchPage('history', this)">
            <svg viewBox="0 0 24 24"><path d="M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>
            Records
        </button>
        <button class="nav-item" onclick="switchPage('webview', this)">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
            Browser
        </button>
    </div>
</div>

<script>
    function switchPage(pageName, btnElement) {
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.getElementById('page-' + pageName).classList.add('active');
        if (btnElement) btnElement.classList.add('active');
    }

    function loadWebsite() {
        let url = document.getElementById('urlInput').value.trim();
        const frame = document.getElementById('webFrame');
        const placeholder = document.getElementById('iframePlaceholder');
        if (!url) return;
        if (!url.startsWith('http://') && !url.startsWith('https://')) { url = 'https://' + url; }
        frame.src = url;
        placeholder.style.display = 'none';
    }

    function updateTable(historyList) {
        let h = "";
        historyList.forEach(item => {
            h += `<tr>
                    <td style="font-weight:900; color:#ffaa00; font-family:'Orbitron';">#${item.period}</td>
                    <td style="font-weight:900; color:#f3e8ff; font-family:'Orbitron';">${item.number}</td>
                    <td>${item.status}</td>
                   </tr>`;
        });
        document.getElementById('session-h').innerHTML = h;
    }

    async function fetchGameStatus() {
        try {
            const response = await fetch('/api/game/status');
            const data = await response.json();
            
            document.getElementById('nextP').innerText = data.period ? String(data.period).slice(-4) : '----';
            
            let sec = data.time_remaining;
            document.getElementById('timer').innerText = "00:" + (sec < 10 ? '0' + sec : sec);
            
            document.getElementById('res').innerText = data.result_type || 'SCAN';
            document.getElementById('lvlTag').innerText = "LEVEL " + (data.level || 1);
            document.getElementById('n1').innerText = data.predicted_number !== undefined ? data.predicted_number : '?';

            if (data.history && data.history.length > 0) {
                updateTable(data.history);
            }
        } catch (err) {
            console.error("API Error:", err);
        }
    }

    setInterval(fetchGameStatus, 1000);
    fetchGameStatus();
</script>
</body>
</html>
"""

def send_telegram_message(message, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = requests.post(url, json=payload, timeout=5)
        res_json = response.json()
        if not res_json.get("ok"):
            print(f"Telegram Send Error: {res_json.get('description')}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def send_telegram_sticker(is_win):
    sticker_id = WIN_STICKER_ID if is_win else LOSS_STICKER_ID
    if not sticker_id or "..." in sticker_id:
        fallback_text = "🎉 RESULT: WIN ✅" if is_win else "❌ RESULT: LOSS ❌"
        send_telegram_message(fallback_text)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
    payload = {
        "chat_id": CHANNEL_ID,
        "sticker": sticker_id
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        res_json = response.json()
        if not res_json.get("ok"):
            print(f"Telegram Sticker Error: {res_json.get('description')}")
            fallback_text = "🎉 RESULT: WIN ✅" if is_win else "❌ RESULT: LOSS ❌"
            send_telegram_message(fallback_text)
    except Exception as e:
        print(f"Error sending Telegram sticker: {e}")

def fetch_live_wingo_history():
    try:
        global WINGO_API_URL
        url = WINGO_API_URL + f"&_={int(time.time()*1000)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            list_data = data.get("data", {}).get("list", []) or data.get("list", [])
            return list_data
    except Exception as e:
        print(f"Live API Error: {e}")
    return []

def parse_item_num(item):
    try:
        num = item.get("number") or item.get("openCode") or item.get("Number", 0)
        return int(num)
    except:
        return 0

def generate_number_for_type(pred_type):
    import random
    if pred_type == "BIG":
        return random.choice([5, 6, 7, 8, 9])
    else:
        return random.choice([0, 1, 2, 3, 4])

def get_ai_level1_prediction(history_list):
    import random
    if not history_list or len(history_list) < 5:
        return random.choice(["BIG", "SMALL"])
    
    recent = history_list[:10]
    big_count = sum(1 for item in recent if item.get("actual_type") == "BIG")
    small_count = len(recent) - big_count
    
    if big_count >= small_count:
        return "BIG"
    else:
        return "SMALL"

def prediction_worker():
    global latest_data, stats_counter
    print("🚀 Ultra-Stable AI Engine Started...")
    
    last_processed_issue = ""
    last_prediction = None
    current_level = 1

    while True:
        try:
            now = datetime.datetime.now()
            seconds_remaining = 60 - now.second

            live_list = fetch_live_wingo_history()

            if live_list and isinstance(live_list, list) and len(live_list) > 0:
                latest_issue_item = live_list[0]
                issue_num = str(latest_issue_item.get("issueNumber") or latest_issue_item.get("periodNumber") or latest_issue_item.get("IssueNumber") or "")
                
                if issue_num:
                    open_num = parse_item_num(latest_issue_item)
                    actual_size = "BIG" if open_num >= 5 else "SMALL"

                    # 1. Evaluate previous round safely before clearing reference
                    prev_type_saved = None
                    if last_prediction and str(last_prediction.get("period")) == issue_num:
                        prev_type_saved = last_prediction.get("type")
                        is_win = (actual_size == prev_type_saved)
                        
                        if is_win:
                            stats_counter["wins"] += 1
                        else:
                            stats_counter["losses"] += 1

                        status_str = '<span class="tag-win">✅ WIN ✅</span>' if is_win else '<span class="tag-loss">❌ LOSS ❌</span>'

                        send_telegram_sticker(is_win)

                        latest_data["history"].insert(0, {
                            "period": issue_num[-4:],
                            "number": open_num,
                            "actual_type": actual_size,
                            "status": status_str
                        })
                        if len(latest_data["history"]) > 10:
                            latest_data["history"].pop()

                        # Level management based on win/loss
                        if is_win:
                            current_level = 1
                        else:
                            current_level += 1
                            if current_level > 4:
                                current_level = 1

                        last_prediction = None

                    # 2. Generate next prediction safely on issue change
                    if issue_num != last_processed_issue:
                        last_processed_issue = issue_num
                        print(f"📥 New Game Issue Detected: {issue_num}")
                        
                        try:
