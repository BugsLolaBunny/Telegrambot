import logging
import pandas as pd
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Загружаем данные из Excel
try:
    df = pd.read_excel("users.xlsx")
except FileNotFoundError:
    logging.error("Файл users.xlsx не найден. Убедитесь, что он в той же папке, что и скрипт.")
    exit(1)

# Приводим "Номер счётчика" к строковому типу
df["Номер счётчика"] = df["Номер счётчика"].astype(str).str.strip()

# Хэндлер для /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне номер счётчика, и я верну лицевой счёт и ФИО."
    )

# Хэндлер для сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meter_number = update.message.text.strip()
    logging.info(f"Запрос по счётчику: {meter_number}")

    result = df[df["Номер счётчика"] == meter_number]

    if result.empty:
        await update.message.reply_text("Счётчик не найден. Проверьте номер.")
    else:
        lines = []
        for _, row in result.iterrows():
            fio = str(row.get('ФИО', '')).strip()

            raw_account = row.get('Лицевой счет', '')
            if pd.isna(raw_account):
                account = ''
            elif isinstance(raw_account, float) and raw_account.is_integer():
                account = str(int(raw_account))
            else:
                account = str(raw_account).strip()

            lines.append(f"👤 {fio}  🔢 {account}")

        response = "Результаты поиска:\n" + "\n".join(lines)
        await update.message.reply_text(response)

# Точка входа
if __name__ == "__main__":
    TOKEN = "7793615747:AAFwpellAf-o6WYMgDolQZCglS9yqzEJk4k"  # Замените на свой токен

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
