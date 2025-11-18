import os
from schedule import get_schedule
import telebot
from dotenv import load_dotenv
import json
import datetime
from api_weather import get_weather 

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
API_WEATHER_TOKEN = os.getenv('API_WEATHER_TOKEN')
INFO = 'Список команд:\n  * /start - Запустить бота\n  * /schedule - Открыть расписание\n  * /change_group - Изменить группу\n  * /get_weather - Узнать погоду\n  * /change_city - Изменить город(для погоды)\n  * /help или "справка" - Справка'

if __name__=='__main__':
    bot = telebot.TeleBot(API_TOKEN)

    @bot.message_handler(func=lambda message: message.text and message.text.startswith('/'))
    def handle_commands(message):
        # bot.clear_step_handler_by_chat_id(message.chat.id)
        if message.text.lower() == '/start':
            start(message)
        elif message.text.lower() == '/help' or message.text.lower() == 'справка':
            info(message)
        elif message.text.lower() == '/get_weather':
            ask_city(message)
        elif message.text.lower() == '/change_city':
            change_city(message)
        elif message.text.lower() == '/change_group':
            change_group(message)
        elif message.text.lower() == '/schedule':
            getting_group_name(message)

    
    # @bot.message_handler(commands=['start'])
    def start(message):
        '''Срабатывает при старте'''
        bot.reply_to(message, f'Привет, товарищ!\n{INFO}')
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        user_id = str(message.from_user.id)
        if user_id not in users:
            users[user_id] = {"group" : None, "city" : None}  # каркас
            with open('users.json', 'w', encoding='utf-8') as f:
                json.dump(users, f)
    

    # @bot.message_handler(commands=['help'], func=lambda message: message.text == 'справка')
    def info(message):
        bot.reply_to(message, INFO)
    
    
    # @bot.message_handler(commands=['get_weather'])
    def ask_city(message):
        bot.clear_step_handler_by_chat_id(message.chat.id)
        user_id = str(message.from_user.id)
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        if users[user_id]["city"] != None:
                # сразу открываем погоду
                city = users[user_id]["city"]
                #функция для получения погоды, которая отправит в нормальном виде
                status_code, weather = get_weather(city, API_WEATHER_TOKEN)
                
                bot.reply_to(message, f'{city} | {weather}')
        else:
            sent = bot.reply_to(message, 'Введите название города')
            bot.register_next_step_handler(sent, get_weather_by_city)
    
    
    def get_weather_by_city(message):
        if message.text.startswith('/'):
            handle_commands(message)
        else:
            city = message.text.strip().capitalize()
            # проверить статус код и если что попросить ввести заново
            try:
                status_code, weather = get_weather(city, API_WEATHER_TOKEN)
            except:
                status_code = 404
            if status_code == 404:
                sent = bot.reply_to(message, 'Нет информации о таком городе, вы уверены, что не ошиблись? 😔\nПопробуйте еще раз!')
                bot.register_next_step_handler(sent, get_weather_by_city)
            else:
                bot.reply_to(message, f'{city} | {weather}')
                
                with open('users.json', 'r', encoding='utf-8') as f:
                    users = json.load(f)
                users[str(message.from_user.id)]["city"] = city

                with open('users.json', 'w', encoding='utf-8') as f:
                    json.dump(users, f, ensure_ascii=False, indent=2)
    
    
    # @bot.message_handler(commands=['change_city'])
    def change_city(message):
        '''проверяет есть ли город или нет'''
        user_id = str(message.from_user.id)
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        if users[user_id]["city"] != None:
            users[user_id]["city"] = None
            #вот тут запись происходит
            with open('users.json', 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2) 

            getting_new_changed_city(message)
        else:
            bot.reply_to(message, 'Нет данных о городе. Для начала вызовите погоду(/get_weather) и введите город.')


    def getting_new_changed_city(message):
        '''Просит ввести город'''
        sent = bot.reply_to(message, 'Введите название города', reply_markup= telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent, change_city)

    
    def changing_city(message):
        '''Изменение группы в БД'''
        if message.text.startswith('/'):
            handle_commands(message)
        else:
            city = message.text.strip().capitalize()  # ввод пользователя
            
            status_code, weather = get_weather(city, API_WEATHER_TOKEN)
            
            if status_code == 404:
                sent = bot.reply_to(message, 'Нет информации о таком городе, вы уверены, что не ошиблись? 😔\nПопробуйте еще раз!')
                bot.register_next_step_handler(sent, changing_city)
            else:
                with open('users.json', 'r', encoding='utf-8') as f:
                    users = json.load(f)
                users[str(message.from_user.id)]["city"] = city

                with open('users.json', 'w', encoding='utf-8') as f:
                    json.dump(users, f, ensure_ascii=False, indent=2)
            
                bot.reply_to(message, 'Город успешно изменен! 😎')
    
    
    @bot.message_handler(func=lambda message: message.text.lower()=='чат')
    def send_chat_info(message):
        '''Отправляет имя пользователя.
        для тестирования'''
        bot.reply_to(message, str(message.from_user.id))

    
    # @bot.message_handler(commands=['change_group'])
    def change_group(message):
        '''Проверяет есть ли такая группа, если нет, то нет смысла менять пустоту'''
        user_id = str(message.from_user.id)
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        if users[user_id]["group"] != None:
            users[user_id]["group"] = None
            #вот тут запись происходит
            with open('users.json', 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2) 

            getting_new_changed_group(message)
        else:
            bot.reply_to(message, 'Нет данных о группе. Для начала вызовите расписание(/schedule) и введите группу.')

    
    def getting_new_changed_group(message):
        '''Просит ввести номер группы'''
        sent = bot.reply_to(message, 'Введите название группы. Например: ИТ2304(Изменение группы)', reply_markup= telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent, changing_group)

    
    def changing_group(message):
        '''Изменение группы в БД'''
        if message.text.startswith('/'):
            handle_commands(message)
        else:
            group = message.text.strip().upper()  # ввод пользователя
            
            if get_schedule(group) == None: # словарь вида {'2025-11-15': 'text'}
                sent = bot.send_message(message.chat.id, 'Данные о группе неверные, введите в похожем формате: ИТ2304')
                bot.register_next_step_handler(sent, changing_group)
            else:
                with open('users.json', 'r', encoding='utf-8') as f:
                    users = json.load(f)
                users[message.from_user.username]["group"] = group
                #вот тут запись происходит
                with open('users.json', 'w', encoding='utf-8') as f:
                    users = json.dump(users, f, ensure_ascii=False, indent=2)
                
                bot.reply_to(message, 'Группа успешно изменена! 😎')


    # @bot.message_handler(commands=['schedule'])
    def getting_group_name(message):
        '''Получаем или выводим название группы'''
        user_id = str(message.from_user.id)
        with open('users.json', 'r', encoding='utf-8') as file:
            users = json.load(file) 
        if users[user_id]["group"] != None: 
            getting_choice(message)
        else:
            sent = bot.reply_to(message, 'Введите название группы. Например: ИТ2304', reply_markup= telebot.types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, new_group)
    

    def new_group(message):
        '''Добавление номера группы'''
        if message.text.startswith('/'):
            handle_commands(message)
        else:
            group = message.text.strip().upper()  # от пользователя

            if get_schedule(group) == None: # словарь вида {'2025-11-15': 'text'}
                sent = bot.send_message(message.chat.id, 'Данные о группе неверные, введите в похожем формате: ИТ2304')
                bot.register_next_step_handler(sent, new_group)
            else:
                with open('users.json', 'r', encoding='utf-8') as f:
                    users = json.load(f)
                users[str(message.from_user.id)]["group"] = group
                #вот тут запись происходит
                with open('users.json', 'w', encoding='utf-8') as f:
                    users = json.dump(users, f, ensure_ascii=False, indent=2)    

                getting_choice(message)
    
    
    def getting_choice(message):
        '''Создает кнопки и просит выбрать расписание'''
         
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

        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        schedule = get_schedule(users[str(message.from_user.id)]["group"])
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