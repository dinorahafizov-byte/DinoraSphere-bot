import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.environ.get("BOT_TOKEN")

CHANNELS = ["@Din_koreakosmetika", "@D_lingu"]
PRIVATE_CHANNEL_ID = -1003512316765
ADMINS = [123456789]
REQUIRED = 8
DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "used": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


data = load_data()

TEXT = (
    "Online til markazimizga xush kelibsiz 😍\n\n"
    "👇 Arab tilidan TEKIN kurs\n"
    "🎯 8 ta odam olib keling va sovg‘ani oling!\n\n"
)


async def is_subscribed(bot, uid: int) -> bool:
    for ch in CHANNELS:
        member = await bot.get_chat_member(ch, uid)
        if member.status in ["left", "kicked"]:
            return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if uid not in data["users"]:
        data["users"][uid] = {"count": 0, "reward": False}

        if context.args:
            ref = context.args[0]
            key = f"{ref}>{uid}"

            if (
                ref != uid
                and ref in data["users"]
                and key not in data["used"]
                and data["users"][ref]["count"] < REQUIRED
            ):
                data["users"][ref]["count"] += 1
                data["used"].append(key)
                save_data(data)

                await context.bot.send_message(
                    int(ref),
                    f"🎉 Sizning linkingiz orqali "
                    f"{data['users'][ref]['count']} ta odam qo‘shildi!\n"
                    f"📊 {data['users'][ref]['count']}/{REQUIRED}"
                )

    save_data(data)

    keyboard = [
        [InlineKeyboardButton("📢 1-kanal", url="https://t.me/Din_koreakosmetika")],
        [InlineKeyboardButton("📢 2-kanal", url="https://t.me/D_lingu")],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check")]
    ]

    await update.message.reply_text(
        "👋 Avval barcha kanallarga obuna bo‘ling 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = str(q.from_user.id)

    if not await is_subscribed(context.bot, int(uid)):
        await q.message.reply_text("❌ Avval barcha kanallarga obuna bo‘ling.")
        return

    link = f"https://t.me/{context.bot.username}?start={uid}"
    count = data["users"][uid]["count"]

    await q.message.reply_text(
        TEXT +
        f"🔗 Sizning shaxsiy linkingiz:\n{link}\n\n"
        f"📊 Natija: {count}/{REQUIRED}"
    )

    if count >= REQUIRED and not data["users"][uid]["reward"]:
        invite = await context.bot.create_chat_invite_link(
            chat_id=PRIVATE_CHANNEL_ID,
            member_limit=1
        )
        data["users"][uid]["reward"] = True
        save_data(data)

        await context.bot.send_message(
            int(uid),
            f"🎉 TABRIKLAYMIZ!\n\n"
            f"🎁 Yopiq kanal linki:\n{invite.invite_link}"
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check, pattern="check"))

    print("🤖 Bot ishga tushdi")
    app.run_polling()


if __name__ == "__main__":
    main()
