import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
OXAPAY_MERCHANT_KEY = os.getenv("OXAPAY_MERCHANT_KEY", "")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))
SHOP_SLOT_PRICE = float(os.getenv("SHOP_SLOT_PRICE", "50"))
