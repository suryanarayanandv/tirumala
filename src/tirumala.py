import json, hashlib, os, re, requests

URL = "https://ttdevasthanams.ap.gov.in/cms/api/universal-latest-updates?populate=*"
STATE_FILE = "seen.json"
BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
CHAT_ID   = os.environ["TG_CHAT_ID"]

def fetch_updates():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    items = []
    for block in r.json()["data"]:
        for u in block["attributes"]["update"]:
            text = u["data"].strip()
            print(f"text: {text}")
            # turn markdown links [Click Here](/path) into full URLs
            text = re.sub(r"\[([^\]]+)\]\((/[^)]+)\)",
                          r"\1: https://ttdevasthanams.ap.gov.in\2", text)
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
    main()