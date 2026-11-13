import json, hashlib, os, re, requests
import sys

URL = "https://ttdevasthanams.ap.gov.in/cms/api/universal-latest-updates?populate=*"
STATE_FILE = "seen.json"
BOT_TOKEN = os.environ["TG_BOT_TOKEN"]   # from @BotFather
CHAT_ID   = os.environ["TG_CHAT_ID"]

import time

def fetch_updates():
    last_err = None
    for attempt in range(4):                      # try up to 4 times
        try:
            r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            r.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            last_err = e
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(15 * (attempt + 1))        # wait 15s, 30s, 45s...
    else:
        raise ConnectionError(f"TTD site unreachable after 4 tries: {last_err}")

    items = []
    for block in r.json()["data"]:
        for u in block["attributes"]["update"]:
            text = u["data"].strip()
            text = re.sub(r"\[([^\]]+)\]\((/[^)]+)\)",
                          r"\1: https://ttdevasthanams.ap.gov.in\2", text)
            text = text.replace("**", "")
            items.append({"id": u["id"], "text": text,
                          "hash": hashlib.md5(text.encode()).hexdigest()})
    return items

def notify(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": msg[:4000]})

def main():
    seen = json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else None
    current = fetch_updates()
    new_state = {str(i["id"]): i["hash"] for i in current}

    if seen is not None:  # skip alerts on the very first run
        for i in current:
            old = seen.get(str(i["id"]))
            if old is None:
                notify("🆕 New TTD update:\n\n" + i["text"])
            elif old != i["hash"]:
                notify("✏️ TTD update changed:\n\n" + i["text"])

    json.dump(new_state, open(STATE_FILE, "w"))

if __name__ == "__main__":
    try:
        main()
    except ConnectionError as e:
        # Network problem: skip this check, don't spam Telegram, don't fail the run
        print(f"::warning::{e}")
        sys.exit(0)
    except Exception as e:
        # Anything else (e.g. TTD changed the data format) is a real problem: alert
        notify(f"⚠️ TTD watcher error: {e}")
        sys.exit(1)