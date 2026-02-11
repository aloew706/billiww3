
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler, CallbackQueryHandler

NAME, EMAIL = range(2)
users = {}

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Каталог"), KeyboardButton("Корзина")],
        [KeyboardButton("Промокоды"), KeyboardButton("Реф система")],
        [KeyboardButton("Личный кабинет")]
    ],
    resize_keyboard=True
)



catalog = [
    {"name": "Джинсы", "desc": "Качественные джинсы из денима.", "price": "1500₽", "photo": "https://i.imgur.com/0Zz23Tk.jpg"},
    {"name": "Ковбойская шляпа", "desc": "Стильная ковбойская шляпа.", "price": "2000₽", "photo": "https://i.imgur.com/w3jS7eK.jpg"},
    {"name": "Трусы", "desc": "Удобные хлопковые трусы.", "price": "500₽", "photo": "https://i.imgur.com/8g7rKma.jpg"},
    {"name": "Кожанка", "desc": "Модная кожаная куртка.", "price": "7000₽", "photo": "https://i.imgur.com/sBGd6BV.jpg"},
    {"name": "Ботинки со шпорами", "desc": "Кожаные ботинки с шпорами.", "price": "3500₽", "photo": "https://i.imgur.com/u7TJ0a7.jpg"},
    {"name": "Рубашка", "desc": "Лёгкая хлопковая рубашка.", "price": "1200₽", "photo": "https://i.imgur.com/cWTVmfA.jpg"},
    {"name": "Кепка", "desc": "Спортивная кепка.", "price": "800₽", "photo": "https://i.imgur.com/F4e6wEb.jpg"},
    {"name": "Пояс", "desc": "Кожаный ремень.", "price": "900₽", "photo": "https://i.imgur.com/3MrgMHE.jpg"},
    {"name": "Шарф", "desc": "Тёплый шерстяной шарф.", "price": "1100₽", "photo": "https://i.imgur.com/DWKOcWl.jpg"},
    {"name": "Перчатки", "desc": "Зимние кожаные перчатки.", "price": "1300₽", "photo": "https://i.imgur.com/DPjWF0z.jpg"},
]

def get_catalog_keyboard(index: int) -> InlineKeyboardMarkup:
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"catalog_{index-1}"))
    buttons.append(InlineKeyboardButton("Выбрать", callback_data=f"select_{index}"))
    if index < len(catalog) - 1:
        buttons.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f"catalog_{index+1}"))
    buttons.append(InlineKeyboardButton("Выйти", callback_data="catalog_exit"))
    return InlineKeyboardMarkup([buttons])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в магазин одежды!\nВыберите действие:",
        reply_markup=main_keyboard,
    )

async def personal_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        cursor.execute("SELECT name, email FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            users[user_id] = {"name": row[0], "email": row[1]}

    if user_id in users:
        user = users[user_id]
        text = (f"Ваш профиль:\n"
                f"Имя: {user['name']}\n"
                f"Email: {user['email']}\n\n"
                f"Чтобы обновить данные, отправьте /register")
    else:
        text = "Вы не зарегистрированы.\nЧтобы пройти регистрацию, отправьте /register"
    await update.message.reply_text(text)

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, введите ваше имя:")
    return NAME

async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("Введите ваш email:")
    return EMAIL

async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if "@" not in email or '.' not in email:
        await update.message.reply_text("Некорректный email. Попробуйте ещё раз:")
        return EMAIL

    context.user_data['email'] = email
    user_id = update.effective_user.id
    name = context.user_data['name']

    cursor.execute("REPLACE INTO users (user_id, name, email) VALUES (?, ?, ?)", (user_id, name, email))
    conn.commit()

    users[user_id] = {"name": name, "email": email}
    await update.message.reply_text("Регистрация успешно завершена!", reply_markup=main_keyboard)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Регистрация отменена.", reply_markup=main_keyboard)
    return ConversationHandler.END

async def placeholders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пока тут ничего нет.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Неизвестная команда или сообщение. Используйте кнопки меню.")

async def catalog_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = 0
    item = catalog[index]
    text = f"*{item['name']}*\n{item['desc']}\nЦена: {item['price']}"
    await update.message.reply_photo(
        photo=item['photo'],
        caption=text,
        parse_mode='Markdown',
        reply_markup=get_catalog_keyboard(index)
    )

async def catalog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "catalog_exit":
        await query.message.edit_caption("Выход из каталога.", reply_markup=None)
        await query.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_keyboard)
        return

    if data.startswith("catalog_"):
        index = int(data.split("_")[1])
        item = catalog[index]
        text = f"*{item['name']}*\n{item['desc']}\nЦена: {item['price']}"
        await query.message.edit_media(
            media=InputMediaPhoto(media=item['photo'], caption=text, parse_mode='Markdown'),
            reply_markup=get_catalog_keyboard(index)
        )
        return

    if data.startswith("select_"):
        index = int(data.split("_")[1])
        item = catalog[index]
        await query.answer()  
        await query.message.reply_text(
            f"Вы выбрали товар:\n*{item['name']}*\nЦена: {item['price']}",
            parse_mode='Markdown',
            reply_markup=main_keyboard
        )
    

def main():
    TOKEN = ""
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex('^Личный кабинет$'), personal_area))
    app.add_handler(MessageHandler(filters.Regex('^Каталог$'), catalog_start))
    app.add_handler(MessageHandler(filters.Regex('^(Корзина|Промокоды|Реф система)$'), placeholders))
    app.add_handler(CallbackQueryHandler(catalog_callback, pattern='^(catalog_|select_|catalog_exit)$'))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.add_handler(MessageHandler(filters.TEXT, unknown))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
