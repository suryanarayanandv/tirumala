# 🛕 TTD Latest Updates Watcher

Get a **Telegram notification** whenever new announcements appear in the
"Latest Updates" section of the official
[Tirumala Tirupati Devasthanams booking portal](https://ttdevasthanams.ap.gov.in/home/dashboard),
such as darshan ticket releases, accommodation quotas, seva E-Dip results and more.

> ⚠️ **Disclaimer:** This is an unofficial, personal project and is **not affiliated with TTD**.
> It reads the same public data the TTD website loads in your browser. TTD may change or
> remove this data source at any time. Always confirm details on the official website.

---

## How it works

```
cron-job.org (every 10 min) ──► GitHub Actions ──► fetch TTD updates feed
                                                        │
                                          compare with seen.json
                                                        │
                                       new / changed? ──► Telegram message 📩
```

- **Data source:** `https://ttdevasthanams.ap.gov.in/cms/api/universal-latest-updates?populate=*`
- **State:** `seen.json` stores a fingerprint (hash) of each update, so you only get notified about new or edited ones.
- **Scheduler:** [cron-job.org](https://cron-job.org) triggers the workflow every 10 minutes. GitHub's built-in schedule is too unreliable for this.

---

## Project structure

```
.
├── .github/
│   └── workflows/
│       └── watch.yml      # GitHub Actions workflow
├── src/
│   └── tirumala.py        # The watcher script
├── seen.json              # Auto-generated state file (don't edit)
└── README.md
```

---

## Setup guide

You'll need:

- A [GitHub](https://github.com) account
- A [Telegram](https://telegram.org) account
- A free [cron-job.org](https://cron-job.org) account

### Step 1: Fork this repository

1. Click **Fork** at the top right of this page.
2. Keep the fork **Public**. Public repos get unlimited free GitHub Actions minutes, while private repos get only 2,000 minutes a month and checking every 10 minutes needs about 4,300.
3. In your fork, open the **Actions** tab and click **"I understand my workflows, go ahead and enable them"**. GitHub disables workflows on forks by default.
4. *(Optional)* Delete `seen.json` from your fork so your first run sends a "watcher started" message.

---

### Step 2: Create a Telegram bot

📖 Official docs: [Telegram Bots introduction](https://core.telegram.org/bots) ·
[Creating a bot with BotFather](https://core.telegram.org/bots/features#botfather) ·
[Bot API reference](https://core.telegram.org/bots/api)

1. In Telegram, open **[@BotFather](https://t.me/BotFather)** (check for the blue verified tick).
2. Send `/newbot`.
3. Choose a **display name**, e.g. `TTD Updates Alert`.
4. Choose a **username** that ends in `bot`, e.g. `my_ttd_updates_bot`.
5. BotFather replies with your **bot token**, which looks like this:
   ```
   123456789:AAExampleTokenDoNotShare_xxxxxxxxxxx
   ```

> 🔐 **Keep your token secret.** Anyone with it can control your bot.
> Never commit it to code, paste it in issues or share it in chats.
> If it leaks, send `/revoke` to @BotFather to get a new one.

---

### Step 3: Get your Telegram chat ID

The bot needs to know **where** to send messages.

1. Open your new bot in Telegram (search for its username), tap **Start**, and send any message, e.g. `hi`.
2. In your browser, open this link with your token in place of `<YOUR_BOT_TOKEN>`:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   📖 Docs: [`getUpdates`](https://core.telegram.org/bots/api#getupdates)
3. Find this part in the response:
   ```json
   "chat": { "id": 123456789, "first_name": "...", "type": "private" }
   ```
   That number is your **chat ID**.

**Troubleshooting**

| Problem | Fix |
|---|---|
| `{"ok":true,"result":[]}` (empty) | You haven't messaged the bot yet, or more than 24 hours have passed since you did. Send a new message to **your bot** (not BotFather) and refresh. |
| Still empty | A webhook may be set. Open `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook` once, message the bot again, and refresh. |
| `{"ok":false,"error_code":401}` | The token is wrong. Copy it again from @BotFather. |

**Want alerts in a group or channel?**

- **Group:** Add the bot to the group and send a message there. The chat ID is negative, e.g. `-987654321`.
- **Channel:** Add the bot as an **admin** of the channel and post something. The chat ID looks like `-1001234567890`.

---

### Step 4: Add secrets to GitHub

📖 Docs: [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)

In your fork, go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Name | Value |
|---|---|
| `TG_BOT_TOKEN` | Your bot token from Step 2 |
| `TG_CHAT_ID` | Your chat ID from Step 3 (numbers only, include the `-` for groups/channels) |

Secrets are encrypted and hidden from logs, so they're safe even in a public repo.

---

### Step 5: Test the workflow manually

1. Go to **Actions → TTD Update Watcher → Run workflow**.
2. Within about 30 seconds you should get a Telegram message:
   ```
   ✅ TTD watcher started. Tracking N updates.
   ```
3. A `seen.json` file appears in your repo. That means it's working.

**Test a "new update" alert:** Edit `seen.json`, delete one line (keep the JSON valid) and run the workflow again. You should get a `🆕 New TTD update` message.

---

### Step 6: Create a GitHub token for cron-job.org

📖 Docs: [Managing personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

1. Go to **GitHub → Profile picture → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Configure it:
   - **Name:** `cron-job-ttd`
   - **Expiration:** 90 days or 1 year. ⏰ Set a reminder to renew it.
   - **Repository access:** *Only select repositories* → your fork
   - **Permissions → Repository permissions → Actions:** **Read and write**
3. Click **Generate token** and copy it (it starts with `github_pat_`).

This token can **only** start workflows in this one repository.

---

### Step 7: Schedule it with cron-job.org

📖 Docs: [Create a workflow dispatch event (GitHub API)](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event)

1. Sign up at [cron-job.org](https://cron-job.org) and click **Create cronjob**.
2. **Common tab:**
   - **Title:** `TTD watcher`
   - **URL:**
     ```
     https://api.github.com/repos/<your-username>/<your-repo>/actions/workflows/watch.yml/dispatches
     ```
   - **Execution schedule:** Every 10 minutes
3. **Advanced tab:**
   - **Request method:** `POST`
   - **Headers:**

     | Key | Value |
     |---|---|
     | `Accept` | `application/vnd.github+json` |
     | `Authorization` | `Bearer <your-github-token>` |
     | `X-GitHub-Api-Version` | `2022-11-28` |
     | `Content-Type` | `application/json` |

   - **Request body:**
     ```json
     {"ref":"master"}
     ```
     Use `main` instead if that's your default branch.
4. Click **Test run**. A response of **`204 No Content`** means success, and a new run should appear in your Actions tab.
5. **Save** the cronjob. *(Optional)* Turn on cron-job.org's failure notifications so you know if the token expires.

**Troubleshooting**

| Response | Meaning |
|---|---|
| `401` | The token is wrong or expired, or `Bearer ` is missing before it |
| `403` | The token lacks **Actions: Read and write** or doesn't have access to this repo |
| `404` | The username, repo name or workflow filename in the URL is wrong |
| `422` | The branch name in the body is wrong |

---

## Customisation

**Only get alerts for specific topics:** In `src/tirumala.py`, add this as the first line inside the `for i in current:` loop:

```python
if not any(k.lower() in i["text"].lower() for k in ["darshan", "accommodation"]): continue
```

**Change the check frequency:** Edit the schedule in cron-job.org. Please don't check more often than every 5 minutes, to be respectful to TTD's servers.

---

## FAQ

**I see `⚠️ ... unreachable after 4 tries` warnings in Actions.**
GitHub's servers (mostly in the US) sometimes can't reach the TTD site. The script retries and skips that check without failing. Occasional warnings are normal.

**I'm getting too many messages / duplicate messages.**
Make sure the `schedule:` section is removed from `watch.yml`, so cron-job.org is the only trigger.

**Notifications suddenly stopped.**
Check, in order: whether your GitHub token expired (cron-job.org shows 401), whether the Actions tab shows errors, and whether the bot token was revoked.

**Is my bot token safe in a public repo?**
Yes, as long as it's stored in **GitHub Secrets** and not written in any file.

---

## Credits

- Data: [Tirumala Tirupati Devasthanams](https://ttdevasthanams.ap.gov.in), the official portal
- Scheduler: [cron-job.org](https://cron-job.org) ([source](https://github.com/pschlan/cron-job.org))
- Notifications: [Telegram Bot API](https://core.telegram.org/bots/api)
