# TODO:
# 1. Admin-команды
# 2. ?

from aiogram import Bot, Dispatcher, executor, types
import logging
import sqlite3
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime
import aioschedule
import asyncio



connect = sqlite3.connect("base.db")
cursor = connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS affairs (
    affair VARCHAR(256),
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER(11)
    )""")

logging.basicConfig(level=logging.INFO)
bot = Bot(token="5172964049:AAFrvny8WcjjeCJbhB7btgWg9E8JjKgnsCo")
dp = Dispatcher(bot)
p2p = QiwiP2P(auth_key="eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6Inc0dW5jai0wMCIsInVzZXJfaWQiOiI3OTgwMzI1MzMzNSIsInNlY3JldCI6IjNjNTYzNGM1YjZkM2IzYTJhOTJmNzliNDQwNjMzYzNlZTc5M2U5NTdiZDk5OTY2ODA5OGZkYjZlYzkwNWYxNDEifX0=")

def affair_add(affair, id):
    connect = sqlite3.connect("base.db")
    cursor = connect.cursor()
    cursor.execute("""INSERT INTO affairs (affair, user_id) VALUES (?, ?)""", [affair, id])
    connect.commit()
    connect.close() 
def affair_delete(affair, id):
    connect = sqlite3.connect("base.db")
    cursor = connect.cursor()
    info = cursor.execute("""SELECT affair FROM affairs WHERE affair = ?""", [affair])
    h_affair = info.fetchall()
    if len(h_affair) == 1:
        cursor.execute("""DELETE FROM affairs WHERE user_id = ? AND affair = ?""", [id, affair])
        connect.commit()
        connect.close() 
        return "Дело \"" + str(affair) + "\" удалено"
    else: 
        return "Вы не добавляли такого дела!"

def finish_affair(affair, id):
    connect = sqlite3.connect("base.db")
    cursor = connect.cursor()
    info = cursor.execute("""SELECT affair FROM affairs WHERE affair = ?""", [affair])
    h_affair = info.fetchall()
    if len(h_affair) == 1:
        cursor.execute("""DELETE FROM affairs WHERE user_id = ? AND affair = ?""", [id, affair])
        connect.commit()
        connect.close() 
        return "Дело \"" + str(affair) + "\" завершено!"
    else: 
        return "Вы не добавляли такого дела!"

        

def affair_show(id):
    connect = sqlite3.connect("base.db")
    cursor = connect.cursor()
    cursor.execute("""SELECT affair FROM affairs WHERE user_id = ?""", [id])
    affairs = cursor.fetchall()
    result = "Список дел:\n"
    count = 1
    for affair in affairs:
        result += str(count)+". "+str(affair[0]) + "\n"
        count += 1
    return result

def donate(amount):
    lifetime = 15 
    comment = 'На развитие' 
    bill = p2p.bill(amount=amount, lifetime=lifetime, comment=comment) 
    return f'Сумма: {amount}\nСсылка живет: {lifetime} минут\nСсылка:\n{bill.pay_url}'

def insert_id_to_bd(id):
    connect = sqlite3.connect("base.db")
    cursor = connect.cursor()
    cursor.execute("""INSERT INTO affairs (user_id) VALUES (?)""", [id])
    connect.commit()
    connect.close()

def get_users_id():
    connect = sqlite3.connect("base.db")
    cursor = connect.cursor()
    cursor.execute("""SELECT user_id FROM affairs""")
    users_ids = cursor.fetchall()
    users = []
    for user in users_ids:
        users.append(user[0])
    return users

def get_user_affairs_count(user_id):
    connect = sqlite3.connect("base.db")
    cursor = connect.cursor()
    cursor.execute("""SELECT COUNT(affair) FROM affairs WHERE user_id = ?""", [user_id])
    result = cursor.fetchall()
    return result[0][0]


btn_add_affair = "💼Добавить новое дело💼"
btn_donate = "$ Донатик на развитие $"
btn_show_affair = "💼Просмотреть ваши дела💼"
btn_delete_affair = "❌Удалить дело❌"
btn_finish_affair = "🌟Завершить дело🌟"
btn_info = "?Информация?"
start_menu = ReplyKeyboardMarkup(resize_keyboard=True)
start_menu.add(btn_donate, btn_add_affair, btn_show_affair, btn_delete_affair, btn_finish_affair, btn_info)

@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    id = message.from_user.id
    insert_id_to_bd(id)
    await bot.send_message(message.from_user.id, "Привет! Я Бот для дел! Пиши в меня свои дела, а я запомню и напомню тебе, когда пора будет их выполнять!\nКоманды:\nУдалить дело -- /del <дело, которое хотите удалить>\nДобавить дело -- /add <ваше дело>\nЗавершить дело -- /finish <дело, которое хотите завершить>\nОповещения о ваших невыполненных делах приходят в 8:30\nИнформация -- /info", reply_markup=start_menu)


@dp.message_handler()
async def bot_message(message: types.Message):
    if message.text == "💼Добавить новое дело💼":
        await bot.send_message(message.from_user.id, "Чтобы добавить новое дело введите команду: '/add <ваше дело>'")
    if message.text == "?Информация?":
        await bot.send_message(message.from_user.id, "Команды:\nУдалить дело -- /del <дело, которое хотите удалить>\nДобавить дело -- /add <ваше дело>\nЗавершить дело -- /finish <дело, которое хотите завершить>\nИнформация -- /info\nОповещения о ваших невыполненных делах приходят в 8:30\nЕсли вдруг пропали кнопки, напишите команду /start ")
    if message.text == "/info":
        await bot.send_message(message.from_user.id, "Команды:\nУдалить дело -- /del <дело, которое хотите удалить>\nДобавить дело -- /add <ваше дело>\nЗавершить дело -- /finish <дело, которое хотите завершить>\nИнформация -- /info\nОповещения о ваших невыполненных делах приходят в 8:30\nЕсли вдруг пропали кнопки, напишите команду /start ")    
    if message.text == "💼Просмотреть ваши дела💼":
        id = message.from_user.id
        await bot.send_message(message.from_user.id, affair_show(id))
    if message.text == "❌Удалить дело❌":
        await bot.send_message(message.from_user.id, "Чтобы удалить дело введите команду: '/del <дело, которое хотите удалить>'")
    if message.text == "🌟Завершить дело🌟":
        await bot.send_message(message.from_user.id, "Чтобы завершить дело введите команду: '/finish <дело, которое хотите завершить>'")
    if "/add" in message.text.lower() and message.text.lower().replace("/add", "").strip() != None:
        id = message.from_user.id
        affair = message.text.lower().replace("/add", "").strip()
        affair_add(affair, id)
        await bot.send_message(message.from_user.id, "Ваше дело успешно добавлено!")
    if message.text == "$ Донатик на развитие $":
        await bot.send_message(message.from_user.id, "Напишите команду: '/donate <сумма платежа>' чтобы поддержать меня денюжкой")
    if "/donate" in message.text.lower():
        amount = message.text.lower().replace("/donate", "").strip()
        await bot.send_message(message.from_user.id, donate(amount)+'\nСпасибо за донатик!')
    if "/del" in message.text.lower():
        id = message.from_user.id
        affair = message.text.lower().replace("/del", "").strip()
        await bot.send_message(message.from_user.id, affair_delete(affair, id))
    if "/finish" in message.text.lower():
        id = message.from_user.id
        affair = message.text.lower().replace("/finish", "").strip()
        await bot.send_message(message.from_user.id, finish_affair(affair, id))
    if "/time" in message.text.lower():
        amount = message.text.lower().replace("/time", "").strip()
        await bot.send_message(message.from_user.id, "11")
    if message.text == "/adminmode c_users":
        id = message.from_user.id
        await bot.send_message(message.from_user.id, "В ваш бот заходили " + str(len(get_users_id())) + " пользователей")


async def notifications():
    for user in set(get_users_id()):
        if get_user_affairs_count(user) == 1:   
            await bot.send_message(user, "У вас есть " + str(get_user_affairs_count(user)) + " невыполненное дело!")
        if get_user_affairs_count(user) >= 5:   
            await bot.send_message(user, "У вас есть " + str(get_user_affairs_count(user)) + " невыполненных дел!")
        else:
            await bot.send_message(user, "У вас есть " + str(get_user_affairs_count(user)) + " невыполненных дела!")

async def scheduler():
    aioschedule.every(60).minutes.do(notifications)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
        
async def on_startup(dp): 
    asyncio.create_task(scheduler())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)










