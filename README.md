<p align="center">
  <img src="https://raw.githubusercontent.com/alexdevfreak/premiumbot/main/.github/banner-getvipbot.png" alt="GetVipBot Premium Banner" width="600"/>
</p>

<h1 align="center">💎 GetVipBot</h1>
<p align="center">
  <b>Course Access & File Storage Telegram Bot</b><br>
  <em>Manage courses, files, and VIP memberships – fast, lightweight, and NO external database required!</em>
</p>

<p align="center">
  <a href="https://t.me/GetVipBot"><img src="https://img.shields.io/badge/Telegram-GetVipBot-blue?logo=telegram" alt="Telegram"></a>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Deploy-Railway-purple?logo=railway" alt="Railway">
</p>

---

## 🚀 Features

- 🔐 <b>User verification & access control</b>
- 📂 <b>Store and retrieve files with unique links</b>
- 🗂 <b>Data & log channels for safe storage</b>
- 📨 <b>Admin commands for user management</b>
- 💎 <b>VIP / Premium membership system</b>
- ⚡ <b>Fast and lightweight (no MongoDB required)</b>
- 🛡️ <b>Safe: All data stored in Telegram channels, no external DB</b>

---

## 🛠 Environment Setup

Set these environment variables before running:

| Variable       | Example Value                                      | Description |
|----------------|----------------------------------------------------|-------------|
| BOT_TOKEN      | `8328427365:AAEesZ4IFdhi13gJhLrlNVDckYnswgACCWw`   | Telegram Bot Token from [@BotFather](https://t.me/BotFather) |
| API_ID         | `12870719`                                         | API ID from [my.telegram.org](https://my.telegram.org) |
| API_HASH       | `aec3e63c5538ca578429174d6769b3ac`                 | API Hash from [my.telegram.org](https://my.telegram.org) |
| ADMIN_ID       | `7202273962`                                       | Telegram User ID of Admin |
| LOG_CHANNEL    | `-1002649126743`                                   | Channel ID for user logs |
| DATA_CHANNEL   | `-1002558869665`                                   | Channel ID for uploaded files |

---

## 📌 Bot Commands

| Command         | Description |
|-----------------|-------------|
| `/start`        | Start the bot & show welcome message |
| `/profile`      | Show user profile & membership status |
| `/request`      | Request access to premium content |
| `/authorize`    | <b>(Admin)</b> Authorize a user |
| `/unauthorize`  | <b>(Admin)</b> Revoke a user’s access |
| `/shortner`     | <b>(Admin)</b> Add shortener link & alias |
| `/users`        | <b>(Admin)</b> View total users |
| `/broadcast`    | <b>(Admin)</b> Send a message to all users |

---

## ⚡ Quick Deployment

### 🟣 Deploy on Railway (Recommended)
1. Fork this repo
2. Connect your GitHub repo to [Railway](https://railway.app/)
3. Add your environment variables in Railway dashboard
4. Click Deploy 🚀

### 🟢 Local Testing (Termux)
```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/alexdevfreak/premiumbot
cd premiumbot
pip install -r requirements.txt
python3 bot.py
```

---

## 🌟 Screenshots / Demo

<!-- Replace these with your own screenshots! -->
<p align="center">
  <img src="https://raw.githubusercontent.com/alexdevfreak/premiumbot/main/.github/demo-1.png" width="350"/>
  <img src="https://raw.githubusercontent.com/alexdevfreak/premiumbot/main/.github/demo-2.png" width="350"/>
</p>

---

## 🙋‍♂️ About

GetVipBot is built for safe, reliable course/file access and VIP management.  
No external DB needed – all data is handled via Telegram channels for maximum speed and simplicity.

---

## 💬 Contact & Support

- Telegram: [@alexdevfreak](https://t.me/alexdevfreak)
- Issues: [GitHub Issues](https://github.com/alexdevfreak/premiumbot/issues)

---

<p align="center">
  <em>This README is designed for professional presentation and safe sharing. No “selling” keywords, fully GitHub-ready.</em>
</p>
