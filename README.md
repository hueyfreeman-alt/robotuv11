# Telegram Shop Bot

Python Telegram shop bot built with aiogram, SQLite, and Docker.

## Required environment variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_numeric_telegram_user_id
DB_PATH=/app/data/shop.db

OXAPAY_MERCHANT_API_KEY=your_oxapay_merchant_api_key
OXAPAY_CALLBACK_URL=https://your-domain.com/webhooks/oxapay
OXAPAY_RETURN_URL=https://your-domain.com
OXAPAY_CURRENCY=
OXAPAY_SANDBOX=false

WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8080
```

- `TOKEN` comes from BotFather.
- `ADMIN_ID` is your numeric Telegram user ID. This user can open `/admin`.
- `DB_PATH` should stay `/app/data/shop.db` when running with Docker Compose so the SQLite database is stored in the mounted `./data` folder.
- `OXAPAY_MERCHANT_API_KEY` comes from OxaPay Merchant Service.
- `OXAPAY_CALLBACK_URL` must be a public HTTPS URL that points to this bot, usually `https://your-domain.com/webhooks/oxapay`.
- `OXAPAY_RETURN_URL` is where OxaPay redirects the customer after payment.
- `OXAPAY_CURRENCY` can stay empty if bot prices are in dollars.
- `OXAPAY_SANDBOX=true` enables OxaPay sandbox mode for testing.
- `WEBHOOK_PORT` is the local HTTP port exposed by Docker Compose.

## Deploy on a VPS with Docker Compose

From the project folder on the VPS:

```bash
mkdir -p data
cp .env.example .env
nano .env
docker compose up -d --build
```

The OxaPay webhook endpoint is:

```text
/webhooks/oxapay
```

OxaPay requires a public HTTPS callback URL. On a VPS, put Nginx, Caddy, Cloudflare Tunnel, or another reverse proxy in front of Docker and forward HTTPS traffic to `localhost:8080`.

Health check:

```bash
curl http://localhost:8080/health
```

Check logs:

```bash
docker compose logs -f bot
```

Restart after changes:

```bash
docker compose up -d --build
```

Stop the bot:

```bash
docker compose down
```

## Data persistence

Docker Compose mounts:

```yaml
./data:/app/data
```

The bot stores SQLite data at `/app/data/shop.db`, so products, users, orders, and settings survive container rebuilds.

Back up the database regularly:

```bash
cp data/shop.db data/shop.db.backup
```

## Notes before production use

- Run only one bot container at a time when using Telegram polling.
- Checkout creates an OxaPay invoice and sends the payment URL to the customer.
- The webhook validates OxaPay's `HMAC` header with `OXAPAY_MERCHANT_API_KEY`.
- The bot only fulfills orders when OxaPay sends invoice status `Paid`.
- SQLite is fine for a small single-instance bot. For heavier usage, consider PostgreSQL.
