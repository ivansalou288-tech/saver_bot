from config import *
def update_streak(user: int, text: str, pluses: list, games: int, plus_count: int):
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    rang = int(cursor.execute('SELECT rang FROM [1002274082016] WHERE tg_id = ?', (user,)).fetchone()[0])
    connection = sqlite3.connect(messages_path)
    cursor = connection.cursor()
    result = cursor.execute('SELECT streak FROM balance_history WHERE user = ? ORDER BY created_at DESC LIMIT 1', (user,)).fetchone()
    streak_old = int(result[0]) if result and result[0] is not None else 0
    streak_new = streak_old

    plus_number = {4: [75, 30, 35], 3: [60, 65, 30, 35], 2: [60, 65, 30, 35]}
    try:
        if games != len(pluses):
            print('first')
            try:
                sr_plus = sum(int(i) for i in pluses) / games
            except ZeroDivisionError:
                return
            if sr_plus not in plus_number[rang]:
                streak_new = 0

            else:
                streak_new += games
        else:
            print('second')
            for plus in pluses:
                if int(plus) in plus_number[rang]:
                    streak_new += 1
                else:
                    streak_new = 0
    except KeyError:
        return

    # Обновляем стрик в последней записи
    cursor.execute('''
        UPDATE balance_history 
        SET streak = ? 
        WHERE id = (
            SELECT id FROM balance_history 
            WHERE user = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        )
    ''', (streak_new, user))
    connection.commit()
    connection.close()





def update_balans(user: int, balance: int, games: int, streak: int, points: int, message_id: int):
    connection = sqlite3.connect(messages_path)
    cursor = connection.cursor()
    
    # Добавляем новый баланс в историю
    cursor.execute('INSERT INTO balance_history (user, balance, games, streak, points, message_id) VALUES (?, ?, ?, ?, ?, ?)',
                   (user, balance, games, streak, points, message_id))
    
    # Удаляем старые записи, оставляя только последние 3
    cursor.execute('''
        DELETE FROM balance_history 
        WHERE user = ? AND id NOT IN (
            SELECT id FROM balance_history 
            WHERE user = ? 
            ORDER BY created_at DESC 
            LIMIT 3
        )
    ''', (user, user))
    
    connection.commit()
    connection.close()


def get_balance_info(user: int) -> str:
    connection = sqlite3.connect(messages_path)
    cursor = connection.cursor()
    cursor.execute('''
        SELECT balance, games, streak, points 
        FROM balance_history 
        WHERE user = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    ''', (user,))
    result = cursor.fetchone()
    connection.close()
    
    if not result:
        return "Данные не найдены"
    
    balance, games, streak, points = result
    output = f"Баланс {balance}\nКатки {games}"
    
    if streak is not None:
        output += f"\nСтрик {streak}"
    if points is not None:
        output += f"\nБаллы {points}"
    
    return output


def delete_last_balance(user: int) -> bool:
    """Удаляет последний баланс и откатывается к предыдущему. Возвращает True если удаление успешно."""
    connection = sqlite3.connect(messages_path)
    cursor = connection.cursor()
    
    # Проверяем количество записей
    cursor.execute('SELECT COUNT(*) FROM balance_history WHERE user = ?', (user,))
    count = cursor.fetchone()[0]
    
    if count <= 1:
        connection.close()
        return False  # Нельзя удалить последнюю запись
    # mess_id = cursor.execute('SELECT message_id FROM balance_history WHERE user = ? ORDER BY created_at DESC LIMIT 1', (user, )).fetchone()[0]
    # try:
    #     await bot.delete_message(chat_id=8015726709, message_id=mess_id)
    # except Exception as e:
    #     await bot.send_message(chat_id=1240656726, text=e)
    # Удаляем последнюю запись
    cursor.execute('''
        DELETE FROM balance_history 
        WHERE id = (
            SELECT id FROM balance_history 
            WHERE user = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        )
    ''', (user,))
    
    connection.commit()
    connection.close()
    return True
    
def transver(from_user: int, to_user: int, sum: int):
    ...

 
async def send_msg(message_old: str, message_new: Union[str, None], user_fullname: str, user_id: int, bot: Bot = None):
    if message_new is None:
        msg = (f' <b>Пользователь {user_fullname} ({user_id})</b>\n'
               f' <b>Сообщение удалено:</b>\n'
               f' Сообщение:\n<code>{message_old}</code>\n')
    else:
        msg = (f' <b>Пользователь {user_fullname} ({user_id})</b>\n'
               f' <b>Сообщение изменено:</b>\n'
               f' Старое сообщение:\n<code>{message_old}</code>\n'
               f' Новое сообщение:\n<code>{message_new}</code>')
    await bot.send_message(USER_ID, msg, parse_mode='html')
 


@router.message()
async def start(message: Message, bot: Bot):
    if message.from_user.id != 1240656726:
        return
    
    try:
        text = message.text.split('.влад')[1]
        id = 5694090404
        connection = sqlite3.connect(messages_path)
        cursor = connection.cursor()
        conn = cursor.execute('SELECT id FROM connections WHERE user = ?', (id, )).fetchone()[0]

        await bot.send_message(chat_id=8015726709, business_connection_id=conn, text=text)

    except IndexError:
        return
 
@router.business_connection()
async def handler_connection(con: BusinessConnection, bot: Bot):
    connection_id = con.id
    user_id = con.user.id
    connection = sqlite3.connect(messages_path)
    cursor = connection.cursor()
    try:
        cursor.execute('INSERT INTO connections (user, id) VALUES (?, ?)', (user_id, connection_id))
        connection.commit()
    except sqlite3.IntegrityError:
        cursor.execute('UPDATE connections SET id = ? WHERE user = ?', (connection_id, user_id))
        connection.commit()
    await bot.send_message(user_id, f'Бот подключеyн к бизнес-аккаунту. ID подключения: {connection_id}')


@router.edited_business_message()
async def edited_business_message(message: types.Message, bot: Bot):
    connection = sqlite3.connect(messages_path)
    cursor = connection.cursor()
    user_id = cursor.execute('SELECT user FROM connections WHERE id = ?', (message.business_connection_id,)).fetchone()[0]

    result = cursor.execute("SELECT text, photo, video, voice, audio, document, video_note FROM messages WHERE mess = ? AND conn = ? AND chat = ?", 
                           (message.message_id, message.business_connection_id, message.chat.id)).fetchone()
    
    if not result:
        connection.close()
        return
    
    user_link = f'[{message.chat.full_name}](https://t.me/{message.chat.username})'
    old_text, old_photo, old_video, old_voice, old_audio, old_document, old_video_note = result
    
    new_photo = message.photo[-1].file_id if message.photo else None
    new_video = message.video.file_id if message.video else None
    new_voice = message.voice.file_id if message.voice else None
    new_audio = message.audio.file_id if message.audio else None
    new_document = message.document.file_id if message.document else None
    new_video_note = message.video_note.file_id if message.video_note else None
    
    if old_text != message.text and old_text:
        await bot.send_message(user_id, f'🔏 {user_link} изменил текст:\n\nСтарый:\n```{old_text}```\n\nНовый:\n```{message.text or "(удален)"}```', parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)  
    if old_photo and old_photo != new_photo:
        await bot.send_photo(user_id, old_photo, caption=f'🔏 {user_link} изменил фото', parse_mode=ParseMode.MARKDOWN)
    if old_video and old_video != new_video:
        await bot.send_video(user_id, old_video, caption=f'🔏 {user_link} изменил видео', parse_mode=ParseMode.MARKDOWN)
    if old_voice and old_voice != new_voice:
        await bot.send_voice(user_id, old_voice, caption=f'🔏 {user_link} изменил голосовое', parse_mode=ParseMode.MARKDOWN)
    if old_audio and old_audio != new_audio:
        await bot.send_audio(user_id, old_audio, caption=f'🔏 {user_link} изменил аудио', parse_mode=ParseMode.MARKDOWN)
    if old_document and old_document != new_document:
        await bot.send_document(user_id, old_document, caption=f'🔏 {user_link} изменил документ', parse_mode=ParseMode.MARKDOWN)
    if old_video_note and old_video_note != new_video_note:
        await bot.send_video_note(user_id, old_video_note)
        await bot.send_message(user_id, f'🔏 {user_link} изменил видеосообщение', pparse_mode=ParseMode.MARKDOWN)
    
    cursor.execute("UPDATE messages SET text = ?, photo = ?, video = ?, voice = ?, audio = ?, document = ?, video_note = ? WHERE mess = ? AND conn = ? AND chat = ?",
                   (message.text, new_photo, new_video, new_voice, new_audio, new_document, new_video_note, message.message_id, message.business_connection_id, message.chat.id))
    connection.commit()
    connection.close()
    
 
@router.deleted_business_messages()
async def deleted_business_messages(message: types.Message, bot: Bot):
    connection = sqlite3.connect(messages_path)
    cursor = connection.cursor()
    user_id = cursor.execute('SELECT user FROM connections WHERE id = ?', (message.business_connection_id,)).fetchone()[0]

    
    for message_id in message.message_ids:
        # Проверяем, является ли удаленное сообщение балансом
        balance_result = cursor.execute(
            "SELECT id FROM balance_history WHERE message_id = ? AND user = ?",
            (message_id, user_id)
        ).fetchone()
        
        if balance_result:
            # Это баланс - откатываемся на предыдущий
            cursor.execute(
                "DELETE FROM balance_history WHERE id = ?",
                (balance_result[0],)
            )
            connection.commit()
            
            # Находим предыдущий баланс (пропуская удаленные)
            prev_balance = cursor.execute("""
                SELECT message_id FROM balance_history 
                WHERE user = ? AND message_id IS NOT NULL AND message_id != 0
                ORDER BY created_at DESC 
                LIMIT 1
            """, (user_id,)).fetchone()
            print('tetete')
            if prev_balance and prev_balance[0]:
                try:
                    await bot.pin_chat_message(
                        message.chat.id, 
                        prev_balance[0], 
                        business_connection_id=message.business_connection_id
                    )
                except Exception:
                    pass
            
            await bot.send_message(user_id, f'Баланс откачен на предыдущий:\n{get_balance_info(user_id)}')
            continue
        
        # Обычное сообщение - стандартная обработка
        result = cursor.execute(
            "SELECT text, photo, video, voice, audio, document, video_note FROM messages WHERE mess = ? AND conn = ? AND chat = ?", 
            (message_id, message.business_connection_id, message.chat.id)
        ).fetchone()
        
        if not result:
            continue
            
        user_link = f'[{message.chat.full_name}](https://t.me/{message.chat.username})'
        text, photo, video, voice, audio, document, video_note = result
        
        if text:
            await bot.send_message(user_id, f'🗑 Это сообщение было удалено {user_link}\n\n```{message.chat.full_name}\n\n{text}```', parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        if photo:
            await bot.send_photo(user_id, photo, caption=f'🗑 Это фото было удалено\nОт: {user_link}', parse_mode=ParseMode.MARKDOWN)
        if video:
            await bot.send_video(user_id, video, caption=f'🗑 Это видео было удалено\nОт: {user_link}', parse_mode=ParseMode.MARKDOWN)
        if voice:
            await bot.send_voice(user_id, voice, caption=f'🗑 Это голосовое было удалено\nОт: {user_link}', parse_mode=ParseMode.MARKDOWN)
        if audio:
            await bot.send_audio(user_id, audio, caption=f'🗑 Это аудио было удалено\nОт: {user_link}', parse_mode=ParseMode.MARKDOWN)
        if document:
            await bot.send_document(user_id, document, caption=f'🗑 Это документ было удалено\nОт: {user_link}', parse_mode=ParseMode.MARKDOWN)
        if video_note:
            await bot.send_video_note(user_id, video_note)
            await bot.send_message(user_id, f'🗑 Это видеосообщение было удалено\nОт: {user_link}', parse_mode=ParseMode.MARKDOWN)
    
    connection.close()
    
@router.business_message()
async def business_message(message: types.Message, bot: Bot):








    connection = sqlite3.connect(messages_path)
    cursor = connection.cursor()
    user = cursor.execute('SELECT user FROM connections WHERE id = ?', (message.business_connection_id,)).fetchone()[0]
    # if user != 1240656726:
    #     return
    photo = message.photo[-1].file_id if message.photo else None
    video = message.video.file_id if message.video else None
    voice = message.voice.file_id if message.voice else None
    audio = message.audio.file_id if message.audio else None
    document = message.document.file_id if message.document else None
    video_note = message.video_note.file_id if message.video_note else None
    print(message.business_connection_id)
    cursor.execute("INSERT INTO messages (mess, conn, chat, user, text, photo, video, voice, audio, document, video_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (message.message_id, message.business_connection_id, message.chat.id, user, message.text, photo, video, voice, audio, document, video_note))
    connection.commit()
    
    try:
        text = message.text.lower()
    except Exception:
        return
    # if text == '.восстановить':
    #
    #     result = cursor.execute(
    #         "SELECT text, photo, video, voice, audio, document, video_note FROM results",).fetchall()
    #     for i in result:
    #
    #         text, photo, video, voice, audio, document, video_note = i
    #         user_id  = 1240656726
    #         if text:
    #             await bot.send_message(user_id, text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    #         if photo:
    #             await bot.send_photo(user_id, photo)
    #         if video:
    #             await bot.send_video(user_id, video)
    #         if voice:
    #             await bot.send_voice(user_id, voice)
    #         if audio:
    #             await bot.send_audio(user_id, audio)
    #         if document:
    #             await bot.send_document(user_id, document)
    #         if video_note:
    #             await bot.send_video_note(user_id, video_note)
    #         print('ok')
    #         await asyncio.sleep(1)


    if message.chat.id != 8015726709:
        return

     #* Проверяем на то что сообщение содержит баланс, катки, стрик, бал
    
    
    

    if not text:
        return
    # Команда .бал
    if text == '.бал':
        result = cursor.execute('''
            SELECT message_id FROM balance_history 
            WHERE user = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user,)).fetchone()
        print('tetetee')
        print(result)
        if result and result[0]:
            await bot.send_message(message.chat.id, '.', reply_to_message_id=result[0], business_connection_id=message.business_connection_id)
        try:
            list1 = []
            list1.append(message.message_id)
            await bot.delete_business_messages(business_connection_id=message.business_connection_id, message_ids=list1)
        except Exception as e:
            await bot.send_message(user, f"Failed to delete message: {e}")
        connection.close()
        return
    
    # Команда .удалить - удаляет последний баланс и откатывается к предыдущему
    if text == '.удалить':
        if delete_last_balance(user):
            new_balance_info = get_balance_info(user)
            await bot.send_message(user, f'Последний баланс удален. Откат к предыдущему:\n{new_balance_info}')
        else:
            await bot.send_message(user, 'Невозможно удалить последний баланс. Должна остаться хотя бы одна запись.')
        try:
            list1 = []
            list1.append(message.message_id)
            await bot.delete_business_messages(business_connection_id=message.business_connection_id, message_ids=list1)
        except Exception as e:
            await bot.send_message(user, f"Failed to delete message: {e}")
        connection.close()
        return
    
    is_balance = True

    # Извлекаем баланс
    try:
        balance_part = text.split('баланс ')[1].split()[0]
        balance = int(balance_part.replace('₽', '').replace('р', ''))
    except (IndexError, ValueError):
      is_balance = False
    
    # Извлекаем катки
    try:
        games = int(text.split('катки ')[1].split()[0])
    except (IndexError, ValueError):
        is_balance = False
    
    # Извлекаем стрик
    try:
        streak = int(text.split('стрик ')[1].split()[0])
    except (IndexError, ValueError):
        streak = None
    
    # Извлекаем баллы
    try:
        points = int(text.split('баллы ')[1].split('.')[0])
    except (IndexError, ValueError):
        points = None
    if is_balance:
        update_balans(user, balance, games, streak, points, message.message_id)
        try:
            await bot.pin_chat_message(message.chat.id, message.message_id, business_connection_id=message.business_connection_id)
        except Exception as e:
            await bot.send_message(user, f"Failed to pin message: {e}")
        return
    
    #* Проверяем на то что сообщение содержит +

    if text[0] == '+':
        
        # Проверяем количество знаков '+' и наличие недопустимых символов
        plus_count = text.count('+')
        print(plus_count)
        pluses = []
        games = 0
        
        if plus_count > 1:
            allowed_chars = set(f'0123456789+-*/=.,₽р\n ')
            has_invalid_chars = any(char not in allowed_chars for char in text)
            
            if has_invalid_chars:
                return
            count = 0
            for i in range(plus_count):
                pluss = text.split('+')[i+1].split()[0]
                print(pluss)
                if int(pluss) >= 10:
                    count+=int(pluss)
                    pluses.append(pluss)
                else:
                    games += int(pluss)
        else:
            try:
                count_part = text.split('+')[1].split()[0]
                count = int(count_part.replace('₽', '').replace('р', ''))
            except (IndexError, ValueError):
                return
        
        connection = sqlite3.connect(messages_path)
        cursor = connection.cursor()

        update_streak(user, text, pluses, games, plus_count)
        
        # Получаем текущий баланс
        result = cursor.execute('''
            SELECT balance, games, streak, points 
            FROM balance_history 
            WHERE user = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user,)).fetchone()
        
        if result:
            old_balance, old_games, old_streak, old_points = result
            new_balance = old_balance + count
            new_games = old_games + games
            
            # Создаем новую запись с обновленным балансом
            mess_id = 0
            update_balans(user, new_balance, new_games, old_streak, old_points, mess_id)
            connection.commit()
            mess_id = (await message.answer(get_balance_info(user))).message_id
            cursor.execute('''
                UPDATE balance_history
                SET message_id = ?
                WHERE user = ?
                AND balance = ?
            ''', (mess_id, user, new_balance))
            connection.commit()



            
            await bot.send_message(user, f'Ваш баланс был увеличен на {count}.\n{get_balance_info(user)}')
        
        connection.close()
        try:
            await bot.pin_chat_message(message.chat.id, mess_id, business_connection_id=message.business_connection_id)
        except Exception as e:
            await bot.send_message(user, f"Failed to pin message: {e}")
            return
    
    #* Проверяем на то что сообщение содержит -
    
    if text[0] == '-':
        try:
            count_part = text.split('-')[1].split()[0]
            count = int(count_part.replace('₽', '').replace('р', ''))
        except (IndexError, ValueError):
            return
        
        connection = sqlite3.connect(messages_path)
        cursor = connection.cursor()
        
        # Получаем текущий баланс
        result = cursor.execute('''
            SELECT balance, games, streak, points 
            FROM balance_history 
            WHERE user = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user,)).fetchone()
        
        if result:
            old_balance, old_games, old_streak, old_points = result
            new_balance = old_balance - count
            
            # Создаем новую запись с обновленным балансом
            mess_id = 0
            update_balans(user, new_balance, old_games, old_streak, old_points, mess_id)
            connection.commit()
            mess_id = (await message.answer(get_balance_info(user))).message_id
            cursor.execute('''
                UPDATE balance_history
                SET message_id = ?
                WHERE user = ?
                AND balance = ?
            ''', (mess_id, user, new_balance))
            connection.commit()
            
            try:
                await bot.pin_chat_message(message.chat.id, mess_id, business_connection_id=message.business_connection_id)
            except Exception as e:
                await bot.send_message(user, f"Failed to pin message: {e}")
                return

            if text.split()[1] == 'ежу':
                result = cursor.execute('''
                    SELECT balance, games, streak, points 
                    FROM balance_history 
                    WHERE user = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                ''', (1240656726,)).fetchone()
        
                if result:
                    old_balance, old_games, old_streak, old_points = result
                    new_balance = old_balance + count
                    
                    # Создаем новую запись с обновленным балансом
                    mess_id = 0
                    update_balans(1240656726, new_balance, old_games, old_streak, old_points, mess_id)
                    connection.commit()
                    ezh = cursor.execute('SELECT id FROM connections WHERE user = ?', (1240656726,)).fetchone()[0]
   
                    await bot.send_message(chat_id=8015726709,business_connection_id=ezh, text=f'+{count} от {GetUserByID(user).pubg_nik}(@{GetUserByID(user).username})')
                    mess_id = (await bot.send_message(chat_id=8015726709,business_connection_id=ezh, text=get_balance_info(1240656726))).message_id
                    cursor.execute('''
                        UPDATE balance_history
                        SET message_id = ?
                        WHERE user = ?
                        AND balance = ?
                    ''', (mess_id, 1240656726, new_balance))
                    connection.commit()
            
                    try:
                        await bot.pin_chat_message(message.chat.id, mess_id, business_connection_id=ezh)
                    except Exception as e:
                        await bot.send_message(user, f"Failed to pin message: {e}")
                        return

                
            connection.commit()
            
            await bot.send_message(user, f'Ваш баланс был уменьшен на {count}.\n{get_balance_info(user)}')
        
        connection.close()

        

async def main() -> None:
 
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
 
    dp.include_router(router)
 
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
 
if __name__ == "__main__":

    asyncio.run(main())