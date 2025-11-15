from schedule import get_schedule
import telebot
from config import TOKEN
import json
import webbrowser
API_TOKEN = TOKEN
GROUP = ''


if __name__=='__main__':
    bot = telebot.TeleBot(API_TOKEN)
    url = 'https://vk.com/valerrienikonova'

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(message, 'Привет, товарищ!')


    @bot.message_handler(func=lambda message: message.text.lower()=='чат')
    def send_chat_info(message):
        bot.reply_to(message, message.from_user.username)


    @bot.message_handler(func=lambda m: m.text.lower() == 'вк')
    def open_vk(message):
        webbrowser.open(url, new= 2)


    @bot.message_handler(commands=['schedule'])
    def schedule(message):
        sent = bot.reply_to(message, 'Введите название группы. Например: ИТ2304')
        bot.register_next_step_handler(sent, schedule_choice)
        #вызвать другой обработчик группы


    def schedule_choice(message): 
        global GROUP
        GROUP = message.text  # вот здесь нужно обработать 

       
        result = get_schedule(GROUP)
        if result == None: # словарь вида {'2025-11-15': 'text'}
            bot.send_message(message.chat.id, 'Данные о группе неверные, введите в похожем формате: ИТ2304')
            bot.register_next_step_handler(message, schedule_choice)
        else:
            week = 'first_week'
            date = '2025-11-17'
            for key, value in result[week].items():
                bot.send_message(message.chat.id, value)
            
    
    
    #ДВЕ НЕДЕЛИ    
    #for key, value in result[first_week].items():
                #bot.send_message(message.chat.id, value)
    #for key, value in result[second_week].items():
                #bot.send_message(message.chat.id, value)
    
    
    
    
    
    
    
    
    
    @bot.message_handler(commands=['music'])
    def send_music(message):
        with open(r'D:\Scaletta\Music\Fairy Tail Soundtracks\4.Prelude to Destruction.mp3', 'rb') as music:
            bot.send_audio(message.chat.id, music)
    bot.infinity_polling()