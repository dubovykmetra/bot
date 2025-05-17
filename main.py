import asyncio
from aiogram import Bot, Dispatcher
from handlers import start, add_skin, get_skins
from aiogram.types import BotCommand
from db.database import init_db

BOT_TOKEN = "7869776078:AAFTZtTFOrZ1qrqM8Vkz9S1jiYyKGmBn1zI"

async def main():
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook()
    print("Webhook deleted")
    await bot.session.close()
    dp = Dispatcher()
    
    dp.include_routers(start.router, add_skin.router, get_skins.router)

    init_db()

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="add", description="Добавить скин"),
       # BotCommand(command="select", description="Получить таблицу"),

    ])

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())