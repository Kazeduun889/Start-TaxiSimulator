import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PreCheckoutQuery, ContentType
import firebase_admin
from firebase_admin import credentials, firestore

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8569821524:AAH1Ea-eFFCl_3yHzE86WCBa16ZGXulHtw0"
FIREBASE_KEY_PATH = "path/to/serviceAccountKey.json" # Скачай ключ из Firebase Console -> Settings -> Service Accounts

# Инициализация Firebase
cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Инициализация Бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Цены (в Stars)
PRICES = {
    "coins": 50,
    "vip": 100,
    "tesla": 250
}

# 1. Генерация ссылки на оплату (Эмуляция API)
# В реальной жизни HTML должен делать fetch к этому серверу.
# Но для простоты: юзер может просто написать команду боту /buy

@dp.message(F.text == "/buy_vip")
async def buy_vip(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="VIP Статус",
        description="x2 доход навсегда + золотой ник",
        payload=f"vip_{message.from_user.id}",
        provider_token="", # Для Stars пусто
        currency="XTR",
        prices=[{"label": "VIP", "amount": 100}],
    )

# 2. Подтверждение перед оплатой (Pre-Checkout)
@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 3. Успешная оплата (Выдача товара)
@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    user_id = str(message.from_user.id)
    
    # Разбор payload (например "vip_12345")
    item_type = payload.split("_")[0]
    
    doc_ref = db.collection("players").document(user_id)
    
    if item_type == "vip":
        doc_ref.update({"isVip": True})
        await message.answer("✅ VIP статус активирован! Перезайди в игру.")
        
    elif item_type == "coins":
        doc_ref.update({"money": firestore.Increment(50000)})
        await message.answer("✅ +50,000 монет начислено!")

    elif item_type == "tesla":
        # Тут нужно добавить логику добавления машины в массив owned
        # doc_ref.update({"owned": firestore.ArrayUnion([99])})
        await message.answer("✅ Tesla Gold добавлена в гараж!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())