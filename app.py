import telebot

from app.config import settings


bot = telebot.TeleBot(settings.telegram_token)

@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}, я помощник по оценке ликвидности недвижимости в Москве и Санкт-Петербурге!")


if __name__ == "__main__":
    bot.infinity_polling()