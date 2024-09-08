from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import random
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
import time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('7455855544:AAHjS7MKkBCL9EXXQagw0RcdPnGkwGT8d8k')

user_data = {}

user_settings = {}

def error_handler(update, context):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update.message:
        update.message.reply_text("An error occurred! Please try again later.")

def login(update, context):
    user_id = update.message.from_user.id
    if user_id in user_data:
        update.message.reply_text("You are already logged in!")
    else:
        user_data[user_id] = {'logged_in': True, 'naira': 0, 'referrals': 0}
        update.message.reply_text("You have successfully logged in!")

def logout(update, context):
    user_id = update.message.from_user.id
    if user_id in user_data and user_data[user_id]['logged_in']:
        del user_data[user_id]
        update.message.reply_text("You have successfully logged out!")
    else:
        update.message.reply_text("You are not logged in!")

def spin(update, context):
    user = update.message.from_user
    user_id = user.id

    if user_id not in user_data or not user_data[user_id]['logged_in']:
        update.message.reply_text("Please log in first using /login.")
        return

    cards = [
        ("Card with your game logo", 0),
        ("Share this game with F&M", 0),
        ("1 Naira", 1),
        ("2 Naira", 2),
        ("3 Naira", 3),
        ("4 Naira", 4),
        ("-2 Naira (scary card!)", -2)
    ]

    card, value = random.choice(cards)
    user_data[user_id]['naira'] += value
    update.message.reply_text(f"{user.first_name}, you spun a card and got: {card}. Your Naira balance is now {user_data[user_id]['naira']}.")

def referral(update, context):
    user_id = update.message.from_user.id
    
    if user_id not in user_data or not user_data[user_id]['logged_in']:
        update.message.reply_text("Please log in first using /login.")
        return

    user_data[user_id]['referrals'] += 1
    update.message.reply_text(f"You have successfully referred someone! Total referrals: {user_data[user_id]['referrals']}.")


def balance(update, context):
    user_id = update.message.from_user.id
    
    if user_id not in user_data or not user_data[user_id]['logged_in']:
        update.message.reply_text("Please log in first using /login.")
        return

    naira_balance = user_data[user_id]['naira']
    update.message.reply_text(f"Your current Naira balance is: {naira_balance}")

def status(update, context):
    user_id = update.message.from_user.id
    
    if user_id not in user_data or not user_data[user_id]['logged_in']:
        update.message.reply_text("Please log in first using /login.")
        return

    naira_balance = user_data[user_id]['naira']
    referrals = user_data[user_id]['referrals']
    update.message.reply_text(f"Status:\nBalance: {naira_balance} Naira\nReferrals: {referrals}")

def leaderboard(update, context):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['naira'], reverse=True)
    leaderboard_text = "Leaderboard:\n"
    for user_id, data in sorted_users[:10]:
        try:
            user = context.bot.get_chat(user_id)
            leaderboard_text += f"{user.first_name}: {data['naira']} Naira\n"
        except Exception as e:
            logger.error(f"Error fetching user details: {e}")
    update.message.reply_text(leaderboard_text)

def inline_button_handler(update, context):
    query = update.callback_query
    query.answer()
    choice = query.data
    query.edit_message_text(text=f"Selected option: {choice}")

def send_inline_buttons(update, context):
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='1')],
        [InlineKeyboardButton("Option 2", callback_data='2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def send_keyboard(update, context):
    keyboard = [
        ['Button 1', 'Button 2'],
        ['Button 3']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def scheduled_message(context):
    chat_id = context.job.context['chat_id']
    context.bot.send_message(chat_id=chat_id, text="This is an automatic message.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_message, 'interval', hours=1, context={'chat_id': os.getenv('7197585216')})
    scheduler.start()

def set_setting(update, context):
    user_id = update.message.from_user.id
    if len(context.args) != 2:
        update.message.reply_text("Usage: /setsetting <key> <value>")
        return

    key, value = context.args
    if user_id not in user_settings:
        user_settings[user_id] = {}
    user_settings[user_id][key] = value
    update.message.reply_text(f"Setting {key} updated to {value}")

def get_setting(update, context):
    user_id = update.message.from_user.id
    if user_id not in user_settings or not user_settings[user_id]:
        update.message.reply_text("No settings found.")
        return

    settings = "\n".join(f"{key}: {value}" for key, value in user_settings[user_id].items())
    update.message.reply_text(f"Your settings:\n{settings}")

def handle_rate_limits(update, context):
    try:
        time.sleep(0.05)
    except Exception as e:
        logger.error(f"Rate limit hit: {e}")
        time.sleep(2)

def main():

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("login", login))
    dispatcher.add_handler(CommandHandler("logout", logout))
    dispatcher.add_handler(CommandHandler("spin", spin))
    dispatcher.add_handler(CommandHandler("referral", referral))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("leaderboard", leaderboard))

    dispatcher.add_handler(CallbackQueryHandler(inline_button_handler))
    dispatcher.add_handler(CommandHandler("options", send_inline_buttons))
    dispatcher.add_handler(CommandHandler("keyboard", send_keyboard))

    dispatcher.add_error_handler(error_handler)

    dispatcher.add_handler(CommandHandler("rate_limit", handle_rate_limits))

    dispatcher.add_handler(CommandHandler("setsetting", set_setting))
    dispatcher.add_handler(CommandHandler("getsetting", get_setting))

    start_scheduler()

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
