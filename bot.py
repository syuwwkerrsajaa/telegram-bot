import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

welcome_data = {}

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue

        user_id = member.id
        chat_id = update.effective_chat.id
        name = member.mention_html()

        await context.bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(can_send_messages=False)
        )

        keyboard = [
            [InlineKeyboardButton("✅ Saya sudah baca", callback_data=f"verify_{user_id}")]
        ]

        msg = await update.message.reply_html(
            f"👋 Halo {name}!\n\n"
            "📌 Wajib baca rules dulu ya.\n"
            "Klik tombol di bawah agar bisa chat 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        welcome_data[user_id] = {
            "message_id": msg.message_id,
            "chat_id": chat_id
        }

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == f"verify_{user_id}":
        if user_id in welcome_data:
            chat_id = welcome_data[user_id]["chat_id"]

            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=True)
            )

            try:
                await query.message.delete()
            except:
                pass

            await query.answer("✅ Kamu sudah bisa chat sekarang!")
            del welcome_data[user_id]
    else:
        await query.answer("❌ Ini bukan tombol kamu!", show_alert=True)

async def delete_join_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, delete_join_leave))
app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, delete_join_leave))
app.add_handler(CallbackQueryHandler(button_click))

print("Bot berjalan 24 jam 🚀")
app.run_polling()
