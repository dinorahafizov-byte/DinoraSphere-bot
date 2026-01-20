import os, json, asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command

TOKEN = os.environ.get("BOT_TOKEN")

CHANNELS = ["@Din_koreakosmetika", "@D_lingu"]
PRIVATE_CHANNEL_ID = -1003512316765
REQUIRED = 8
DATA_FILE = "data.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def load():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "used": []}
    return json.load(open(DATA_FILE))

def save(data):
    json.dump(data, open(DATA_FILE, "w"))

data = load()

async def is_subscribed(uid: int):
    for ch in CHANNELS:
        member = await bot.get_chat_member(ch, uid)
        if member.status in ["left", "kicked"]:
            return False
    return True

@dp.message(CommandStart())
async def start(message: Message):
    uid = str(message.from_user.id)
    args = message.text.split()

    if uid not in data["users"]:
        data["users"][uid] = {"count": 0, "reward": False}

        if len(args) > 1:
            ref = args[1]
            key = f"{ref}>{uid}"
            if ref != uid and ref in data["users"] and key not in data["used"]:
                data["users"][ref]["count"] += 1
                data["used"].append(key)
                await bot.send_message(
                    int(ref),
                    f"🎉 Yangi odam qo‘shildi!\n📊 {data['users'][ref]['count']}/{REQUIRED}"
                )

    save(data)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 1-kanal", url="https://t.me/Din_koreakosmetika")],
        [InlineKeyboardButton(text="📢 2-kanal", url="https://t.me/D_lingu")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check")]
    ])

    await message.answer("👋 Avval barcha kanallarga obuna bo‘ling 👇", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "check")
async def check(call: CallbackQuery):
    uid = call.from_user.id

    if not await is_subscribed(uid):
        await call.message.answer("❌ Avval barcha kanallarga obuna bo‘ling.")
        return

    link = f"https://t.me/{(await bot.me()).username}?start={uid}"
    count = data["users"][str(uid)]["count"]

    await call.message.answer(
        f"🎯 8 ta odam chaqiring\n"
        f"📊 Natija: {count}/{REQUIRED}\n\n"
        f"🔗 Sizning linkingiz:\n{link}"
    )

    if count >= REQUIRED and not data["users"][str(uid)]["reward"]:
        invite = await bot.create_chat_invite_link(PRIVATE_CHANNEL_ID, member_limit=1)
        data["users"][str(uid)]["reward"] = True
        save(data)

        await bot.send_message(
            uid,
            f"🎉 TABRIKLAYMIZ!\n🎁 Yopiq kanal linki:\n{invite.invite_link}"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
