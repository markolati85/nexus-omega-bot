# Nexus OKX Trading Bot

This project contains a minimal single-exchange trading bot for OKX with optional GPT-4o decision support.

## Structure

- `src/okx_single_bot.py` – main bot implementation
- `config.json` – basic runtime configuration
- `requirements.txt` – required Python packages

## Running

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your OKX and OpenAI credentials:
   ```text
   OKX_API_KEY=...
   OKX_SECRET=...
   OKX_PASSPHRASE=...
   OPENAI_API_KEY=...
   ```
3. Start the bot:
   ```bash
   python src/okx_single_bot.py
   ```

The bot fetches the current ticker for the configured pair, asks GPT‑4o whether to buy or sell, and executes trades if the confidence threshold is reached. All activity is logged to `okx_bot.log`.
