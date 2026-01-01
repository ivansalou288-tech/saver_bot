import configparser
import json
from typing import Union
from pathlib import Path
 
import asyncio
 
from aiogram import (Router, Bot, Dispatcher,F, types)
from aiogram.types import BusinessConnection, Message
from aiogram.filters import Command
import sqlite3
from aiogram.enums.parse_mode import ParseMode

curent_path = (Path(__file__)).parent.parent
messages_path = curent_path / 'databases' / 'messages.db'
curent_main_path = (Path(__file__)).parent.parent.parent
main_path = curent_main_path / 'chat_manager_bot' / 'databases' / 'Base_bot.db'
# main_path = curent_main_path / 'Zam Helper' / 'databases' / 'Base_bot.db'
import secret

# Add your bot token here
TOKEN = secret.TOKEN
USER_ID = 1240656726
 
router = Router(name=__name__)


connection = sqlite3.connect(main_path, check_same_thread=False)
cursor = connection.cursor()
klan = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('klan',)).fetchall()[0][0])



#? EN: Class to extract user information from a message (reply, mention, or ID)
#* RU: Класс для извлечения информации о пользователе из сообщения (ответ, упоминание или ID)
#? EN: Class to extract user information from a message (reply, mention, or ID)
#* RU: Класс для извлечения информации о пользователе из сообщения (ответ, упоминание или ID)
class GetUserByMessage:
    def __init__(self, message):
        self.message = message
        self.user_id = self.getUserId(self.message)
        # self.self_user_id = self.getSelfUserId(self.message)
        self.username = self.getUsernameByID(self.user_id)
        self.name = self.getNameByID(self.user_id)
        self.pubg_id = self.getPubgidByID(self.user_id)
        self.pubg_nik = self.getPubgNikByID(self.user_id)
        self.nik = self.getNikByID(self.user_id)
        self.rang = self.getRangByID(self.user_id)
        self.last_date = self.getLastDateByID(self.user_id)
        self.date_vhod = self.getDateVhodByID(self.user_id)

    def getUserId(self, message):
        try:
            user_id = int(self.message.text.split('tg://openmessage?user_id=')[1].split()[0])
            return user_id
        except IndexError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass
        try:
            user_id = int(self.message.text.split('@')[1].split()[0])
            return user_id
        except ValueError:
            pass
        except IndexError:
            pass
        try:
            username = (message.text.split('@')[1]).split()[0]
            user_id = int(
                cursor.execute(f"SELECT user_id FROM all_users WHERE username=?", (username,)).fetchall()[0][0])
            return user_id
        except IndexError:
            pass

        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            return user_id
        else:
            return False

    def getUsernameByID(self, user_id):
        try:
            username = cursor.execute(f"SELECT username FROM all_users WHERE user_id=?", (self.user_id,)).fetchall()[0][0]
            return username
        except IndexError:
            return 'Отсутвует'

    def getNameByID(self, user_id):
        try:
            name = cursor.execute(f"SELECT name FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return name
        except IndexError:
            return 'Отсутвует'

    def getPubgidByID(self, user_id):
        try:
            pubg_id = cursor.execute(f"SELECT id_pubg FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return pubg_id
        except IndexError:
            return 'Отсутвует'

    def getPubgNikByID(self, user_id):
        try:
            pubg_nik = cursor.execute(f"SELECT nik_pubg FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return pubg_nik
        except IndexError:
            return 'Отсутвует'
    def getNikByID(self, user_id):
        try:
            nik = cursor.execute(f"SELECT nik FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return nik
        except IndexError:
            return 'Отсутвует'



    def getRangByID(self, user_id):

        try:
            rang = cursor.execute(f"SELECT rang FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return rang
        except IndexError:
            return 'Отсутвует'

    def getLastDateByID(self, user_id):
        try:
            last_date = cursor.execute(f"SELECT last_date FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return last_date
        except IndexError:
            return 'Отсутвует'

    def getDateVhodByID(self, user_id):
        try:
            date_vhod = cursor.execute(f"SELECT date_vhod FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return date_vhod
        except IndexError:
            return 'Отсутвует'


#? EN: Class to get user information by their Telegram ID
#* RU: Класс для получения информации о пользователе по его Telegram ID
#? EN: Class to get user information by their Telegram ID
#* RU: Класс для получения информации о пользователе по его Telegram ID
class GetUserByID:
    def __init__(self, user_id):
        self.user_id = user_id
        self.username = self.getUsernameByID(self.user_id)
        self.name = self.getNameByID(self.user_id)
        self.pubg_id = self.getPubgidByID(self.user_id)
        self.pubg_nik = self.getPubgNikByID(self.user_id)
        self.nik = self.getNikByID(self.user_id)
        self.rang = self.getRangByID(self.user_id)
        self.last_date = self.getLastDateByID(self.user_id)
        self.date_vhod = self.getDateVhodByID(self.user_id)

    def getUsernameByID(self, user_id):
        try:
            username = cursor.execute(f"SELECT username FROM all_users WHERE user_id=?", (self.user_id,)).fetchall()[0][
                0]
            return username
        except IndexError:
            return 'Пользователь'

    def getNameByID(self, user_id):
        try:
            name = cursor.execute(f"SELECT name FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return name
        except IndexError:
            return 'Пользователь'

    def getPubgidByID(self, user_id):
        try:
            pubg_id = int(cursor.execute(f"SELECT id_pubg FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0])
            return pubg_id
        except IndexError:
            return 'Отсутвует'

    def getPubgNikByID(self, user_id):
        try:
            pubg_nik = cursor.execute(f"SELECT nik_pubg FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return pubg_nik
        except IndexError:
            return 'Пользователь'

    def getRangByID(self, user_id):

        try:
            rang = cursor.execute(f"SELECT rang FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return rang
        except IndexError:
            return 'Обычный участник'

    def getLastDateByID(self, user_id):
        try:
            last_date = cursor.execute(f"SELECT last_date FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return last_date
        except IndexError:
            return 'Отсутвует'
    def getNikByID(self, user_id):
        try:
            nik = cursor.execute(f"SELECT nik FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return nik
        except IndexError:
            return 'Отсутвует'

    def getDateVhodByID(self, user_id):
        try:
            date_vhod = cursor.execute(f"SELECT date_vhod FROM [{-(klan)}] WHERE tg_id=?", (self.user_id,)).fetchall()[0][0]
            return date_vhod
        except IndexError:
            return 'Отсутвует'
