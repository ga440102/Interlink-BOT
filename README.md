# Interlink BOT
Interlink BOT

- Register Here : [Interlink](https://interlinklabs.ai/referral?refCode=510001)
- Download App
- Scan Face
- Connect Wallet
- Use Code `510001`

## Features

  - Auto Get Account Information
  - Auto Run With [Proxyscrape Free Proxy](https://proxyscrape.com/free-proxy-list) - `Choose 1`
  - Auto Run With Private Proxy - `Choose 2`
  - Auto Run Without Proxy - `Choose 3`
  - Auto Claim Mining
  - Multi Accounts

## Requiremnets

- Make sure you have Python3.9 or higher installed and pip.

## Instalation

1. **Clone The Repositories:**
   ```bash
   git clone https://github.com/ga440102/Interlink-BOT.git
   ```
   ```bash
   cd Interlink-BOT
   ```

2. **Install Requirements:**
   ```bash
   pip install -r requirements.txt #or pip3 install -r requirements.txt
   ```

## Configuration

- **accounts.json:** You will find the file `accounts.json` inside the project directory. Make sure `accounts.json` contains data that matches the format expected by the script. Here are examples of file formats:
  ```json
    [
        {
            "Email": "your_email_address_1",
            "Passcode": "your_passcode",
            "InterlinkId": "your_interlink_id ( without xxxx@, only number )"
        },
        {
            "Email": "your_email_address_2",
            "Passcode": "your_passcode",
            "InterlinkId": "your_interlink_id ( without xxxx@, only number )"
        }
    ]
  ```

- **proxy.txt:** You will find the file `proxy.txt` inside the project directory. Make sure `proxy.txt` contains data that matches the format expected by the script. Here are examples of file formats:
  ```bash
    ip:port # Default Protcol HTTP.
    protocol://ip:port
    protocol://user:pass@ip:port
  ```

## Setup

```bash
python setup.py #or python3 setup.py
```

## Run

```bash
python bot.py #or python3 bot.py
```

