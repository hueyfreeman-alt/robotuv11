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
```

- `TOKEN` comes from BotFather.
- `ADMIN_ID` is your numeric Telegram user ID. This user can open `/admin`.
- `DB_PATH` should stay `/app/data/shop.db` when running with Docker Compose so the SQLite database is stored in the mounted `./data` folder.

## Deploy on a VPS with Docker Compose

From the project folder on the VPS:

```bash
mkdir -p data
cp .env.example .env
nano .env
docker compose up -d --build
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
- Checkout creates a pending `oxapay` payment record and does not auto-deliver products.
- Add an OxaPay webhook or a manual fulfillment flow before accepting real customer payments.
- SQLite is fine for a small single-instance bot. For heavier usage, consider PostgreSQL.
