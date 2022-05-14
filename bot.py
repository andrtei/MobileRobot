from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, Bot, types, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import datetime
import shif
import os
import json
import sqlite3
import configparser
import requests


config = configparser.ConfigParser()
config.read("settings.ini")
tokenBot = config["bot"]["bot_token"]
hostIP = config["host"]["host_ip"]


bot = Bot(token=tokenBot)
dp = Dispatcher(bot, storage=MemoryStorage())


class DataBase():
    
    def __init__(self):
        self.conn = sqlite3.connect('diplom.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def check_in_db(self, message):
        self.cursor.execute(f'SELECT name FROM users WHERE user_id = {message.from_user.id}')
        return self.cursor.fetchone()
    
    def check_active_order(self, message):
        self.cursor.execute(f'SELECT code FROM orders WHERE user_id={message.from_user.id} AND status=0')
        return self.cursor.fetchone()
    
    def create_new_order(self, orderinfo):
        self.cursor.execute('INSERT INTO orders VALUES (NULL, ?, ?, ?, ?, ?);', orderinfo)
        self.conn.commit()

    def register_new_user(self, userinfo):
        self.cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?);', userinfo)
        self.conn.commit()


class Register(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_adres = State()


class NewOrder(StatesGroup):
    waiting_for_item = State()
    waiting_for_pay = State()



menu_btn = ['Меню', 'Настройка']
product_btn = ['Пицца', 'Мороженное']


def keyboards_create(ListNameBTN, NumberColumns=2):
    keyboards = types.ReplyKeyboardMarkup(row_width=NumberColumns, resize_keyboard=True)
    btn_names = [types.KeyboardButton(text=x) for x in ListNameBTN]
    keyboards.add(*btn_names)
    return keyboards


def crypto_decode(message, code_list):
    hesh = str(db.check_active_order(message)[0]) 
    hesh = json.loads(hesh)
    decode_sql = bytes.decode((shif.decrypt(hesh, code_list[1])))
    return decode_sql


@dp.message_handler()
async def start_message(message : types.Message):
    check = db.check_in_db(message)
    if check is None:
        await message.answer('Для заказа нужно пройти регистрацию!')
        await message.answer('Как к вам обращаться ?')
        await Register.waiting_for_name.set()
    else:
        match message.text:
            case 'Меню' | '/start':
                await message.answer('Добро пожаловать в меню:', reply_markup=keyboards_create(product_btn))
                await NewOrder.waiting_for_item.set()
            case "Настройка":
                await message.answer('Настройки профиля')
            case unknown:
                await message.answer('Не знаю такой команды!')


@dp.message_handler(state=Register.waiting_for_name)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer('Ваш номер телефона ?')
    await Register.next()


@dp.message_handler(state=Register.waiting_for_phone)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(phone = message.text)
    await message.answer('Ваша электронная почта ?')
    await Register.next()  


@dp.message_handler(state=Register.waiting_for_email)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(email = message.text)
    await message.answer('Адресс доставки:')
    await Register.next()  


@dp.message_handler(state=Register.waiting_for_adres)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(adress = message.text)
    user_data = await state.get_data()
    name = user_data['name']
    phone = user_data['phone']
    email = user_data['email']
    adress = user_data['adress']
    user_info = [message.from_user.id, name, phone, email, adress]
    db.register_new_user(user_info)
    await message.answer('Спасибо за регистрацию!', reply_markup=keyboards_create(menu_btn))
    await state.finish() 


@dp.message_handler(state=NewOrder.waiting_for_item)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(item = message.text)
    user_data = await state.get_data()
    item = user_data['item']
    user_id = message.from_user.id
    code = shif.crypto(message)
    date = datetime.date.today()
    
    order_info = [code[0], date, 0, user_id, item]
    db.create_new_order(order_info)
    
    photo = open(f'img/{message.from_user.id}.png', 'rb')
    await bot.send_photo(message.chat.id, photo)
    os.remove(f'img/{message.from_user.id}.png')
    await state.finish()
    decode_sql = crypto_decode(message, code)
    
    url = f'http://{hostIP}/qr_code?code={decode_sql}'
    requests.get(url)
 

if __name__ == '__main__':
    db = DataBase()
    executor.start_polling(dp, skip_updates=True)