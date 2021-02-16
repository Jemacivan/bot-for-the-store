#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

class sqliter:

# Инициализация БД
# db initialization
  def __init__(self, database):
    self.connection = sqlite3.connect(database)
    self.cursor = self.connection.cursor()

# Проверка юзера в БД
#check user in db
  def list_user(self,tg_id):
    with self.connection:
      result = self.cursor.execute('SELECT * FROM `users` WHERE `tg_id` = ?', (tg_id,)).fetchall()
      return bool(len(result))

# Если нет зарегестрирувать \ Регистрация
# if no -> register | register
  def register(self,tg_id,name):
    with self.connection:
      return self.cursor.execute("INSERT INTO `users`(`tg_id`,`name`) VALUES (?,?)",(tg_id,name,))

  def check_tov(self,tov_id):
    with self.connection:
      return self.cursor.execute("SELECT id FROM shop WHERE id = ?",(tov_id)).fetchall()

# Вывести список всех товаров
# List all product
  def list_all(self):
    with self.connection:
      return self.cursor.execute('SELECT id, tovar, price FROM shop').fetchall()

# Подробную инфу на конкретный товар
# list detailed information
  def select_tov(self, rownum):
    with self.connection:
      return self.cursor.execute('SELECT * FROM shop WHERE id = ?', (rownum,)).fetchall()

# Получение фото товара
#get product photo
  def get_ph(self, id: int):
    with self.connection:
      return self.cursor.execute('SELECT photo FROM shop WHERE id = ?', (id,)).fetchone()

# Добавление в БД поседнього выбора юзера
# add last selectet item
  def last_item(self, tg_id, item_id):
    with self.connection:
      return self.cursor.execute('UPDATE `users` SET Last_item = ? WHERE tg_id = ?', (item_id,tg_id,))

# Вывести айди последнего выбраного предмета/товара
# list id last selected item/product
  def list_last_item(self,tg_id):
    with self.connection:
      return self.cursor.execute('SELECT `Last_item` FROM `users` WHERE tg_id = ?', (tg_id,)).fetchall()

#Закрыть соидинение с БД
#Close connection
  def close(self):
    self.connection.close()

###########
# корзина #
###########


#Добавить товар в корзину
#Add product to basket
  def basket_add(self, tg_id, tov_id, name, price):
    with self.connection:
      return self.cursor.execute('INSERT INTO `basket`(tg_id, tov_id, name, price) VALUES(?,?,?,?)',(tg_id, tov_id, name, price,))

# Вывод всего что в корзине
# List basket
  def list_basket(self,tg_id):
    with self.connection:
      return self.cursor.execute('SELECT tov_id, name, price, sum FROM basket WHERE tg_id = ?', (tg_id,)).fetchall()

#Прочитать количество товара
#Read product quantity
  def read_nubers(self,tg_id,tov_id):
    with self.connection:
      return self.cursor.execute("SELECT sum FROM basket WHERE `tg_id` = ? AND `tov_id` = ?",(tg_id, tov_id,)).fetchall()

#Добавить товар
#Write\add product quantity
  def write_numb(self,suma,tg_id,tov_id):
    with self.connection:
      return self.cursor.execute('UPDATE `basket` SET `sum` = ? WHERE tg_id = ? AND tov_id = ?',(suma,tg_id,tov_id,))

#Удалить товар с корзины 
#Remove
  def remove_item(self,tg_id,tov_id):
    with self.connection:
      return self.cursor.execute('DELETE FROM `basket` WHERE tg_id = ? AND tov_id = ?',(tg_id,tov_id,))

#Очистить корзину
#clear basket
  def clear_basket(self,tg_id):
    with self.connection:
      return self.cursor.execute('DELETE FROM `basket` WHERE tg_id = ?',(tg_id,))

#########
#Покупка#
#########
  def check_user_in_orders(self,tg_id):
    with self.connection:
      result = self.cursor.execute('SELECT tg_id FROM `orders` WHERE tg_id = ?',(tg_id,)).fetchall()
      return bool(len(result))
  
  def ordering(self,basket,tg_id):
    with self.connection:
      return self.cursor.execute('INSERT INTO orders(basket, tg_id) VALUES (?,?)',(basket,tg_id,))

  def ordersupd(self,basket,tg_id):
    with self.connection:
      return self.cursor.execute('UPDATE orders SET basket = ? WHERE tg_id = ?',(basket,tg_id,))

  def add_tel_num(self,tg_id,number):
    with self.connection:
      return self.cursor.execute('UPDATE `orders` SET `telephone` = ? WHERE tg_id = ?',(number,tg_id,))

  def add_full_name(self,full_name,tg_id):
    with self.connection:
      return self.cursor.execute('UPDATE `orders` SET `full_name` = ? WHERE tg_id = ?',(full_name,tg_id,))

  def add_address(self,address,tg_id):
    with self.connection:
      return self.cursor.execute('UPDATE `orders` SET `address` = ? WHERE tg_id = ?', (address,tg_id,))

  def send_info(self,tg_id):
    with self.connection:
      return self.cursor.execute('SELECT telephone, full_name, address, basket FROM orders WHERE tg_id = ?',(tg_id,)).fetchall()

###############
# Admin Panel #
###############

  def check_passwd(self):
    with self.connection:
      return self.cursor.execute('SELECT passwd FROM passwd_admin').fetchall()

  def add_adm(self,tg_id):
    with self.connection:
      return self.cursor.execute('INSERT INTO `admin`(tg_id) VALUES (?)',(tg_id,))

  def check_adm(self,tg_id):
    with self.connection:
      result = self.cursor.execute('SELECT tg_id FROM `admin` WHERE tg_id = ?',(tg_id,)).fetchall()
      return bool(len(result))

  def get_last_id(self):
    with self.connection:
      return self.cursor.execute('SELECT id FROM shop WHERE id = (SELECT MAX(id)  FROM shop)').fetchall()

  def insert_photo(self, photo: bytes):
    with self.connection:
      return self.cursor.execute('INSERT INTO shop (photo) VALUES (?)', (photo,))

  def insert_name(self, name, id):
    with self.connection:
      return self.cursor.execute('UPDATE `shop` SET `tovar` = ? WHERE id = ?',(name,id,))

  def insert_price(self, price, id):
    with self.connection:
      return self.cursor.execute('UPDATE `shop` SET `price` = ? WHERE id = ?',(price,id,))

  def insert_desk(self, desk, id):
    with self.connection:
      return self.cursor.execute('UPDATE `shop` SET `deskription` = ? WHERE id = ?',(desk,id,))

  def del_post(self,id):
    with self.connection:
      self.cursor.execute('delete from sqlite_sequence where name="shop"')
      return self.cursor.execute('DELETE FROM `shop` WHERE id = ?',(id,))
      
