import telegram
from telegram import update
import telegram.ext
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters
import os
import logging
from main_db import solution_manual



# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# The API Key we received for our bot
# API_KEY = os.environ.get('TOKEN')
API_KEY = "2135948715:AAF03uHkSDM9IQ7XHlm5TUNK4NMgS_s511k"

PORT = int(os.environ.get('PORT', 8443))

# Create an updater object with our API Key
updater = Updater(API_KEY)
# Retrieve the dispatcher, which will be used to add handlers
dispatcher = updater.dispatcher
# Our states, as integers

SYSSTEP, SUBSYSSTEP, PARTSTEP,DEFECTSTEP, END, CANCEL = range(6)

#=================================================================================================================

solution_dict = {}

class Solution:
    def __init__(self, chatID):
        self.chatID = chatID
        self.system = ""
        self.subsystem = ""
        self.part = ""
#=================================================================================================================

# The entry function
def start(update_obj, context):
  
    list1 = [[telegram.KeyboardButton(text=system)] for system in list(solution_manual.keys())]
    #list1.append([telegram.KeyboardButton(text='QUIT')])
    kb = telegram.ReplyKeyboardMarkup(keyboard=list1,resize_keyboard = True, one_time_keyboard = True)
    chat_id = update_obj.message.chat_id
    solution_dict[chat_id] = Solution(chat_id)

    update_obj.message.reply_text("Which system are you interested in?",reply_markup=kb)

    return SYSSTEP


def sysstep(update_obj, context):
    
    chat_id = update_obj.message.chat_id
    msg = update_obj.message.text
    sol = solution_dict[chat_id]
    sol.system = msg
    
    list1 = [[telegram.KeyboardButton(text=subsystem)] for subsystem in list(solution_manual[sol.system].keys())]
    #list1.append([telegram.KeyboardButton(text='QUIT')])
    kb = telegram.ReplyKeyboardMarkup(keyboard=list1,resize_keyboard = True, one_time_keyboard = True)

    update_obj.message.reply_text("Which subsystem are you interested in?",reply_markup=kb)

    return SUBSYSSTEP


def subsystep(update_obj, context):
    
    chat_id = update_obj.message.chat_id
    msg = update_obj.message.text
    sol = solution_dict[chat_id]
    sol.subsystem = msg
    
    list1 = [[telegram.KeyboardButton(text=part)] for part in list(solution_manual[sol.system][sol.subsystem].keys())]
    #list1.append([telegram.KeyboardButton(text='QUIT')])
    kb = telegram.ReplyKeyboardMarkup(keyboard=list1,resize_keyboard = True, one_time_keyboard = True)

    update_obj.message.reply_text("What is the issue?",reply_markup=kb)

    return PARTSTEP

def partstep(update_obj, context):
    
    chat_id = update_obj.message.chat_id
    msg = update_obj.message.text
    sol = solution_dict[chat_id]
    sol.part = msg    

    solution = solution_manual[sol.system][sol.subsystem][sol.part]
    #list1.append([telegram.KeyboardButton(text='QUIT')])
    #kb = telegram.ReplyKeyboardMarkup(keyboard=list1,resize_keyboard = True, one_time_keyboard = True)

    update_obj.message.reply_text(f"""
    The solution is:

    {solution}

    Please click /start to restart the bot
    """,reply_markup=telegram.ReplyKeyboardRemove())

    return ConversationHandler.END


def cancel(update_obj, context):
    # get the user's first name
    first_name = update_obj.message.from_user['first_name']
    update_obj.message.reply_text(
        f"Okay, no question for you then, take care, {first_name}! Please click /start to start again",\
             reply_markup=telegram.ReplyKeyboardRemove())
    return ConversationHandler.END

def main():


    handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),CommandHandler('help', help)],
        states={
                SYSSTEP: [MessageHandler(Filters.text, sysstep)],
                SUBSYSSTEP: [MessageHandler(Filters.text, subsystep)],
                PARTSTEP: [MessageHandler(Filters.text, partstep)],
                DEFECTSTEP: [MessageHandler(Filters.text, sysstep)],
                END: [MessageHandler(Filters.text, sysstep)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        )
    
    dispatcher.add_handler(handler)

    # # start polling for updates from Telegram
    # updater.start_webhook(listen="0.0.0.0",
    #                         port=PORT,
    #                         url_path=API_KEY,
    #                         webhook_url="https://still-sierra-92948.herokuapp.com/" + API_KEY)
    # updater.idle()

    updater.start_polling()

if __name__ == '__main__':
    main()