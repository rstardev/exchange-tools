# exchange-tools

Small UI tool to scan **Binance/Bybit USDT perpetuals** and rank pairs by:

- price change (%)
- volume change (%)
- funding rate
- open interest

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Notes

- This project uses public endpoints (no keys required).
- Some metrics vary by exchange API availability; missing fields are shown as empty.
