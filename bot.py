#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import config
import io
import time
import logging
import telebot
from telebot import types
from db_conect import sqliter

db_worker = sqliter(config.db_name)

bot = telebot.TeleBot(config.token_userbot)

logger = telebot.logger
if config.debug == False:
  telebot.logger.setLevel(logging.INFO)

else:
  telebot.logger.setLevel(logging.DEBUG)


def list_basket(tg_id):
    db_worker = sqliter(config.db_name)
    raw_data = db_worker.list_basket(tg_id)
    total_price = 0
    for tov_id, name, price, count in raw_data:
      total_price += price * count
    list_bask = '\n'.join(f'Номер товара/id: {p[0]}\nИмя товара: {p[1]}\nЦена: {p[2]}\nКоличество: {p[3]}\n====================\n' for p in raw_data)
    out = str(list_bask)+ "Опщая сумма: " + str(total_price) + config.Currency
    return out
    db_worker.close()

#Обробочик callback_data
@bot.callback_query_handler(func = lambda call: True)
def shop(call):
  #Список товаров
  if call.data == 'shop':
    db_worker = sqliter(config.db_name)
    raw_product = db_worker.list_all()
    db_worker.close()
    #Проверка есть ли товар в БД
    if raw_product != []:
      product ='\n'.join(f'{p[0]}. {p[1]} — {p[2]}{config.Currency}' for p in raw_product)
      #выбор
      ch_tov = bot.send_message(call.message.chat.id, "Выберите цифру товара:\n"+product)
      bot.register_next_step_handler(ch_tov,prod)
    else:
      bot.send_message(call.message.chat.id, "Нет товаров в продаже!")

  elif call.data == 'buyed':
    db_worker = sqliter(config.db_name)
    tg_id = call.from_user.id
    bot.delete_message(call.message.chat.id,call.message.message_id)
    bas_et = list_basket(tg_id)

    if db_worker.check_user_in_orders(tg_id) == True:
      db_worker.ordersupd(bas_et,tg_id)
      print("Update")
    else:
      db_worker.ordering(bas_et, tg_id)
      print("Create")

    db_worker.close()
    yiy = bot.send_message(call.message.chat.id, "Введите номер телефона(пример: 0000001111111)\nВАЖНО: Проверьте номер перед тем как отправить боту")
    bot.register_next_step_handler(yiy,tel_num)
  #Кнопка назад
  elif call.data == 'back':
    db_worker = sqliter(config.db_name)
    raw_product = db_worker.list_all()
    db_worker.close()
    product ='\n'.join(f'{p[0]}. {p[1]} — {p[2]}{config.Currency}' for p in raw_product)

    bot.delete_message(call.message.chat.id,call.message.message_id)
    ch_tov = bot.send_message(call.message.chat.id, "Выберите цифру товара:\n"+product)
    bot.register_next_step_handler(ch_tov,prod)
  #Корзина
  elif call.data == 'basket':
    db_worker = sqliter(config.db_name)
    r = list_basket(call.message.chat.id)
    if r == f'Общая сумма: 0{config.Currency}':
      bot.send_message(call.message.chat.id, 'Корзина пустая')
    else:
      keyboard = types.InlineKeyboardMarkup()
      back =  types.InlineKeyboardButton(text="Назад", callback_data="back")
      buy = types.InlineKeyboardButton(text="Купить", callback_data="buyed")
      clear_basket = types.InlineKeyboardButton(text="Очистить", callback_data="clear_basket")
      keyboard.add(back,buy,clear_basket)
      bot.send_message(call.message.chat.id, r,reply_markup=keyboard)
    db_worker.close()
  #Добавление в корзину
  elif call.data == 'add_basket':
    tg_id = call.from_user.id
    db_worker = sqliter(config.db_name)

    raw_id = db_worker.list_last_item(tg_id)
    tov_id = ''.join(f'{p[0]}' for p in raw_id)

    raw_check = db_worker.read_nubers(tg_id,tov_id)
    check = '\n'.join(f'{p[0]}' for p in raw_check)
    #Если товара нет в корзине:
    # Добавить
    if check == '':
      product_info = db_worker.select_tov(tov_id)

      name = '\n'.join(f'{p[1]}' for p in product_info)
      price = '\n'.join(f'{p[2]}' for p in product_info)

      db_worker.basket_add(tg_id,tov_id,name,price)
    #Увеличить ко-лво
    elif int(check) >= 1:
      add_item = int(check) + 1
      db_worker.write_numb(add_item,tg_id,tov_id)

    else:
      print("Error")

    db_worker.close()
    #Вывести сообщение
    bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Товар был добавлен в корзину")

  #Удаление товара с корзины, если есть
  elif call.data == 'remove_item':
    tg_id = call.from_user.id
    db_worker = sqliter(config.db_name)
    raw_id = db_worker.list_last_item(tg_id)
    tov_id = ''.join(f'{p[0]}' for p in raw_id)
    db_worker.remove_item(tg_id,tov_id)
    db_worker.close()
    bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Товар был удален с корзины")

#Очистить корзину
  elif call.data == 'clear_basket':
    db_worker = sqliter(config.db_name)
    db_worker.clear_basket(call.from_user.id)
    bot.delete_message(call.message.chat.id,call.message.message_id)
    db_worker.close()

  else:
    bot.send_message(call.message.chat.id, "Error")

#Магазин
def prod(call):
  db_worker = sqliter(config.db_name)
  user_input = call.text
  try:
    if user_input.isdecimal() == True:
     check = db_worker.check_tov(user_input)
     db_worker.close()
     if check == []:
        back = types.InlineKeyboardMarkup()
        go_back = types.InlineKeyboardButton(text="Назад", callback_data="back")
        back.add(go_back)
        bot.delete_message(call.chat.id,call.message_id)
        bot.send_message(call.chat.id, "Товар не найден=(",reply_markup=back)
     else:
        db_worker = sqliter(config.db_name)
        keyboard = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text="Назад", callback_data="back")
        remove_basket = types.InlineKeyboardButton(text="Убрать придмет", callback_data="remove_item")
        add_basket = types.InlineKeyboardButton(text="Добавить в корзину", callback_data="add_basket")
        basket = types.InlineKeyboardButton(text="Корзина", callback_data="basket")
        keyboard.add(back,basket,remove_basket,add_basket)

        bot.delete_message(call.chat.id,call.message_id)
        user_id = call.from_user.id
        db_worker.last_item(user_id,user_input)
        raw_description = db_worker.select_tov(user_input)
        description = '\n'.join(f'Имя товара: {p[1]}\nЦена товара: {p[2]}{config.Currency}\nОписание: {p[3]}' for p in raw_description)
        photo = db_worker.get_ph(user_input)[0]
        photo_fp = io.BytesIO(photo)
        bot.send_photo(call.chat.id, photo_fp, description, reply_markup=keyboard)
        db_worker.close()
    else:    
      back_q = types.InlineKeyboardMarkup()
      go_back_q = types.InlineKeyboardButton(text="Назад", callback_data="back")
      back_q.add(go_back_q)
      bot.send_message(call.chat.id, "Братиш если ты думал меня сломать я тебя огорчу=(",reply_markup=back_q)

  except:
    back_q = types.InlineKeyboardMarkup()
    go_back_q = types.InlineKeyboardButton(text="Назад", callback_data="back")
    back_q.add(go_back_q)
    bot.send_message(call.chat.id, "Братиш если ты думал меня сломать я тебя огорчу=(",reply_markup=back_q)

  db_worker.close()
######Добавление заказа######
def tel_num(call):
  tel_num = call.text
  db_worker = sqliter(config.db_name)
  int(tel_num)
  db_worker.add_tel_num(call.from_user.id,tel_num)
  o = bot.send_message(call.chat.id,"Отправьте ФИО")
  bot.register_next_step_handler(o,full_name)
  db_worker.close()

def full_name(call):
  full_name = call.text
  db_worker = sqliter(config.db_name)
  db_worker.add_full_name(full_name,call.from_user.id)
  db_worker.close()
  o = bot.send_message(call.chat.id, "Введите адресс доставки(Новая почта)")
  bot.register_next_step_handler(o,address)

def address(call):
  address = call.text
  db_worker = sqliter(config.db_name)
  db_worker.add_address(address,call.from_user.id)
  bot.send_message(call.chat.id, "Вас наберет наш оператор в течении дня!")
  raw_data = db_worker.send_info(call.from_user.id)
  data = ''.join(f'Номер Телефона: {p[0]}\nФИО: {p[1]}\nАддрес доставки: {p[2]}\nКорзина:\n{p[3]}' for p in raw_data)
  db_worker.clear_basket(call.from_user.id)
  db_worker.close()
  bot.send_message(config.chat_id, str(data))

#Оброботка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
  print("User start bot: " + str(message.from_user.first_name) + '\nLast name: ' + str(message.from_user.last_name) + '\nusername: ' + str(message.from_user.username))
  db_worker = sqliter(config.db_name)
  if(not db_worker.list_user(message.from_user.id)):
    tg_id = message.from_user.id
    name = message.from_user.first_name
    db_worker.register(tg_id, name)
  db_worker.close()

  keyboard = types.InlineKeyboardMarkup()
  buy = types.InlineKeyboardButton(text="Магазин", callback_data="shop")
  donate = types.InlineKeyboardButton(text="Тех. Под.", url=config.help_about)
  basket = types.InlineKeyboardButton(text="Корзина", callback_data="basket")
  keyboard.add(buy, donate, basket)
  bot.send_message(message.chat.id, "Здраствуйте!\nВас приветствует магазин kbourtime\nДанный бот поможет сделать покупку.", reply_markup=keyboard)



@bot.message_handler(commands=['help'])
def help(message):
  help_keyboard = types.InlineKeyboardMarkup()
  inst = types.InlineKeyboardButton(text="Instagram", url=config.instagram)
  help_keyboard.add(inst)
  bot.send_message(message.chat.id, "Developer: @fuksys", reply_markup=help_keyboard)

#Добавление админов по ключу
@bot.message_handler(commands=['admin'])
def admins(message):
  db_worker = sqliter(config.db_name)
  msg = message.text.split()[1:]
  out = ''
  out = ' '.join(str(i) for i in msg)
  str(out)
  get_passwd = db_worker.check_passwd()
  check_pass = ''.join(f'{p[0]}' for p in get_passwd)
  if check_pass == out:
   db_worker.add_adm(message.from_user.id)
   bot.send_message(message.chat.id, "Успешно добавлен администратор!")
  else:
    pass
  db_worker.close()

#Добавить пост
@bot.message_handler(commands=['post'])
def photo(message):
  db_worker = sqliter(config.db_name)
  r = db_worker.check_adm(message.from_user.id)
  if r == True:
    keyboard = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text="Отмена", callback_data="back")
    keyboard.add(cancel)
    uiu = bot.send_message(message.chat.id, "Отправь мне фото для товара. ЭТО ОБЯЗАТЕЛЬНО!", reply_markup=keyboard)
    bot.register_next_step_handler(uiu, set_photo)
  db_worker.close()

def set_photo(message):
  db_worker = sqliter(config.db_name)
  try:
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    db_worker.insert_photo(downloaded_file)
    print("Photo added")
    o = bot.send_message(message.chat.id,"Окей. Теперь напиши мне название товара. ЭТО ОБЯЗАТЕЛЬНО!")
    bot.register_next_step_handler(o,set_name)
  except:
    bot.send_message(message.chat.id,'получил что угодно, но определенно не фото')
  db_worker.close()
  
def set_name(message):
  db_worker = sqliter(config.db_name)
  name = message.text
  try:
    str(name)
    raw_lates_id = db_worker.get_last_id()
    lates_id = '\n'.join(f'{p[0]}' for p in raw_lates_id)
    db_worker.insert_name(name,lates_id)
    #
    p = bot.send_message(message.chat.id, "Окей. Теперь напиши мне цену товара. ЭТО ОБЯЗАТЕЛЬНО!")
    bot.register_next_step_handler(p,set_price)
  except:
    bot.send_message(message.chat.id, "Мне не нравится твое сообщение. Попытайся еще раз!")
    bot.register_next_step_handler(message,set_name)
  db_worker.close()

def set_price(message):
  db_worker = sqliter(config.db_name)
  price = message.text
  float(price)
  raw_lates_id = db_worker.get_last_id()
  lates_id = '\n'.join(f'{p[0]}' for p in raw_lates_id)
  db_worker.insert_price(price,lates_id)
  #
  u = bot.send_message(message.chat.id, "Окей. Напиши мне описание товара. ЭТО ОБЯЗАТЕЛЬНО!")
  bot.register_next_step_handler(u,set_desk)
  db_worker.close()

def set_desk(message):
  db_worker = sqliter(config.db_name)
  desk = message.text
  raw_lates_id = db_worker.get_last_id()
  lates_id = '\n'.join(f'{p[0]}' for p in raw_lates_id)
  db_worker.insert_desk(desk,lates_id)
  bot.send_message(message.chat.id, "Пост добавлен")
  db_worker.close()

#Удалить пост
@bot.message_handler(commands=['delpost'])
def del_post(message):
  db_worker = sqliter(config.db_name)
  r = db_worker.check_adm(message.from_user.id)
  if r == True:
    raw_product = db_worker.list_all()
    product ='\n'.join(f'{p[0]}. {p[1]} — {p[2]}{config.Currency}' for p in raw_product)
    ch_tov = bot.send_message(message.chat.id, "Выберите пост который хотите удалить:\n"+product)
    bot.register_next_step_handler(ch_tov,delete_post)
  db_worker.close()

def delete_post(message):
  db_worker = sqliter(config.db_name)
  user_input = message.text
  if user_input.isdecimal() == True:
    check = db_worker.check_tov(user_input)
    if check == []:
      bot.send_message(message.chat.id, "Товар не найден=(")
    else:
      db_worker.del_post(user_input)
      bot.send_message(message.chat.id, "Пост удален!")
  else:
    bot.send_message(message.chat.id, "Что-то ты ввел не так")
  db_worker.close()



#loop
def bot_polling():
  if __name__ == '__main__':
    bot.polling(none_stop = True)

def start_pol():
  if config.auto_restart == True:
    try:
      bot_polling()
    except:
      print('Restart bot 3min')
      time.sleep(180)
      print('Bot restarting')
      start_pol()
  else:
  	bot_polling()


if config.start == True:  	
  start_pol()
else:
  print('Set status "start" true in config.py')