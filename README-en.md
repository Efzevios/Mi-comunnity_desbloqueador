[Português](README.md) | [English](README-en.md) | [Español](README-es.md)

# MIUI Auto Unlock

Python script to automate the Bootloader unlock request on Xiaomi Community (MIUI/HyperOS).
The script runs automatically, bypassing the daily quota limit that resets at 00:00:00 (Beijing time). It automatically handles ping compensation and opens multiple threads so you don't miss the time window.

## Requirements
- Linux (Systemd)
- Python 3.x
- Browser logged into Xiaomi Community Global to get the token

## Installation

1. Clone the repository to your computer:
   ```bash
   git clone https://github.com/YOUR_USERNAME/miui-auto-unlock.git ~/Github/Pessoal/Mi-comunnity_desbloqueador
   ```
2. The script installs Python dependencies automatically (requests, ntplib, pytz, urllib3) if you don't have them.

## How to Use

### 1. Getting the Session Token
For the script to work, it needs to be authenticated to your account.
1. Access the official site: `https://new-ams.c.mi.com/global` and log in.
2. Open Developer Tools (F12) in your browser.
3. Go to the **Storage** > **Cookies** tab.
4. Look for the cookie named `new_bbs_serviceToken`.
5. Copy the value of this cookie and paste it into the `token.txt` file in the script folder, replacing the text `COLE_SEU_TOKEN_AQUI`.

*(Note: The token usually expires in about 24 hours, so it is recommended to update the token daily before midnight in China).*

### 2. Configuring Timeshift
The `timeshift.txt` file is used to compensate for your Ping (latency) to China, triggering the script slightly earlier so that it reaches the server at the exact millisecond.
The default value we left is `351.0` (in milliseconds). You can change this file if you know the exact ping of your server, but the default usually works well for normal connections.

### 3. Running the Script

You can run it manually:
```bash
python3 auto_unlock.py
```

Or, so you don't have to leave the terminal open, I recommend configuring the script as a system service to run in the background:

1. Create the service file at `~/.config/systemd/user/miui-unlock.service` with the following content:

```ini
[Unit]
Description=MIUI Auto Unlock Script

[Service]
Type=simple
ExecStart=/usr/bin/python3 -u %h/Github/Pessoal/Mi-comunnity_desbloqueador/auto_unlock.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=default.target
```

2. Enable and start the service:
```bash
systemctl --user daemon-reload
systemctl --user enable --now miui-unlock.service
```

The script will sleep and wait for the correct time to trigger. Whenever you put a new token in `token.txt`, just run `systemctl --user restart miui-unlock.service` to reload.

---
**Disclaimer:**
This tool was made for personal use and study purposes. There are no guarantees of functionality due to constant changes in Xiaomi servers. Use at your own risk.
