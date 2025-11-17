from schedule import get_schedule
import telebot
from config import TOKEN
import json
import datetime
API_TOKEN = TOKEN

if __name__=='__main__':
    bot = telebot.TeleBot(API_TOKEN)

    
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(message, 'Привет, товарищ!')


    @bot.message_handler(func=lambda message: message.text.lower()=='чат')
    def send_chat_info(message):
        try:
            bot.reply_to(message, message.from_user.username)
        except Exception as e:
            bot.reply_to(message, 'Нет имени пользователя')

    
    @bot.message_handler(commands=['change_group'])
    def change_group(message):
        '''Проверяет есть ли такой пользователь, если нет, то нет смысла менять пустоту'''
        username = message.from_user.username
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        if username in users:
            del users[username]
            with open('users.json', 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2) 
            getting_new_changed_group(message)
        else:
            bot.reply_to(message, 'Нет данных о группе. Для начала вызовите расписание и введите группу.')

    
    def getting_new_changed_group(message):
        '''Изменяет группу и сразу обновляет расписание'''
        sent = bot.reply_to(message, 'Введите название группы. Например: ИТ2304(Изменение группы)', reply_markup= telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent, changing_group)

    
    def changing_group(message):
        group = message.text.upper()  # ввод пользователя
        
        if get_schedule(group) == None: # словарь вида {'2025-11-15': 'text'}
            sent = bot.send_message(message.chat.id, 'Данные о группе неверные, введите в похожем формате: ИТ2304')
            bot.register_next_step_handler(sent, changing_group)
        else:
            with open('users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)
            users[message.from_user.username] = {"group": group}
            with open('users.json', 'w', encoding='utf-8') as f:
                users = json.dump(users, f, ensure_ascii=False, indent=2)


    @bot.message_handler(commands=['schedule'])
    def getting_group_name(message):
        '''Получаем или выводим название группы'''

        with open('users.json', 'r', encoding='utf-8') as file:
            users = json.load(file) 
        if message.from_user.username in users: 
            # sent = bot.send_message(message.chat.id, f'Текущая группа: {users[message.from_user.username]["group"]}')
            # change_group_or_not(sent)
            getting_choice(message)
        else:
            sent = bot.reply_to(message, 'Введите название группы. Например: ИТ2304', reply_markup= telebot.types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, new_group)
        #вызвать другой обработчик группы
    

    def new_group(message):
        '''Добавление номера группы'''
        if message.text == '/schedule':
            # bot.clear_step_handler_by_chat_id(message.chat.id)  # отменяем текущие ожидания
            getting_group_name(message)  # вызываем начальный обработчик
            return 
        
        group = message.text.upper()  # от пользователя

        if get_schedule(group) == None: # словарь вида {'2025-11-15': 'text'}
            sent = bot.send_message(message.chat.id, 'Данные о группе неверные, введите в похожем формате: ИТ2304')
            bot.register_next_step_handler(sent, new_group)
        else:
            with open('users.json', 'r', encoding='utf-8') as f:
                users = json.load(f)
            users[message.from_user.username] = {"group": group}
            with open('users.json', 'w', encoding='utf-8') as f:
                users = json.dump(users, f, ensure_ascii=False, indent=2)    
            getting_choice(message)

    # def change_group_or_not(message):
    #     '''Изменить группу или нет(если пользователь уже вводил группу)'''
    #     if message.text == '/schedule':
    #         # bot.clear_step_handler_by_chat_id(message.chat.id)  # отменяем текущие ожидания
    #         getting_group_name(message)  # вызываем начальный обработчик
    #         return
        
    #     markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    #     btn_y = telebot.types.KeyboardButton('Да')
    #     btn_n = telebot.types.KeyboardButton('Нет')
    #     markup.add(btn_y, btn_n)
    #     sent = bot.send_message(message.chat.id, f'Хотите изменить название группы?', reply_markup=markup)
    #     bot.register_next_step_handler(sent, group_choice)
    
    
    # def group_choice(message):
    #     '''Изменить группу или нет(если пользователь уже вводил группу)'''
    #     if message.text == '/schedule':
    #         bot.clear_step_handler_by_chat_id(message.chat.id)  # отменяем текущие ожидания
    #         getting_group_name(message)  # вызываем начальный обработчик
    #         return
        
    #     if message.text == 'Да' or message.text == 'да' or message.text == 'ДА':
    #         with open('users.json', 'r', encoding='utf-8') as f:
    #             users = json.load(f)
    #         del users[message.from_user.username]
    #         with open('users.json', 'w', encoding='utf-8') as f:
    #             users = json.dump(users, f, ensure_ascii=False, indent=2)
    #         getting_group_name(message)
    #     elif message.text == 'Нет' or message.text == 'нет' or message.text == 'НЕТ':
    #         # обновление расписания
    #         with open('users.json', 'r', encoding='utf-8') as f:
    #             users = json.load(f)
            
    #         schedule = get_schedule(users[message.from_user.username]["group"])
    #         users[message.from_user.username]["schedule"] = schedule
            
    #         with open('users.json', 'w', encoding='utf-8') as f:
    #             users = json.dump(users, f, ensure_ascii=False, indent=2)
    #         getting_choice(message)
    #     else:
    #         sent = bot.reply_to(message, "Введите Да или Нет")
    #         bot.register_next_step_handler(sent, group_choice)
    
    
    def getting_choice(message):
        '''Создает кнопки и просит выбрать расписание'''

        if message.text == '/schedule':
            # bot.clear_step_handler_by_chat_id(message.chat.id)  # отменяем текущие ожидания
            getting_group_name(message)  # вызываем начальный обработчик
            return
         
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        btn_today = telebot.types.KeyboardButton('На сегодня')
        btn_tomorrow = telebot.types.KeyboardButton('На завтра')
        btn_first_week = telebot.types.KeyboardButton('На первую неделю')
        btn_second_week = telebot.types.KeyboardButton('На вторую неделю')
        markup.add(btn_today, btn_tomorrow, btn_first_week, btn_second_week)
                 
        sent = bot.reply_to(message, 'Выберите расписание:', reply_markup=markup)
        bot.register_next_step_handler(sent, final_schedule)

    
    def final_schedule(message):
        '''Отправляет результат'''

        if message.text == '/schedule':
            # bot.clear_step_handler_by_chat_id(message.chat.id)  # отменяем текущие ожидания
            getting_group_name(message)  # вызываем начальный обработчик
            return
        
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        schedule = get_schedule(users[message.from_user.username]["group"])
        text = message.text.strip().capitalize()
        
        if text == 'На сегодня':
            today = datetime.date.today().__str__()
            if today in schedule["first_week"]:
                week = "first_week"
            else:
                week = "second_week"
            bot.reply_to(message, schedule[week][today], reply_markup=telebot.types.ReplyKeyboardRemove())
        
        elif text == 'На завтра':
            tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).__str__()
            if tomorrow in schedule["first_week"]:
                week = "first_week"
            else:
                week = "second_week"
            bot.reply_to(message, schedule[week][tomorrow], reply_markup=telebot.types.ReplyKeyboardRemove())
        elif text == 'На первую неделю':
            week = "first_week"

            for value in schedule[week].values():
                    bot.send_message(message.chat.id, value, reply_markup=telebot.types.ReplyKeyboardRemove())
        elif text == 'На вторую неделю':
            week = "second_week"

            for value in schedule[week].values():
                    bot.send_message(message.chat.id, value, reply_markup=telebot.types.ReplyKeyboardRemove())    
        else:
            sent = bot.reply_to(message, 'Неверный выбор. Должен быть: На сегодня/На завтра/На первую неделю/На вторую неделю')
            bot.register_next_step_handler(sent, final_schedule)

    bot.infinity_polling()
