import os
import json
import logging
from datetime import datetime, time
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Document
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from app.get_random_line import get_random_quote
from db.db_modify import modify_cell
from app.quotes_from_md import parse_md_to_quotes
from db.db_fill_in import db_fill_in
from app.make_pdf import make_pdf

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
SETTING_PERIOD = 1
WAITING_MD_FILE = 2

# Period options
PERIODS = {
    '0': {'name': 'Every minute', 'times': None},  # None indicates every minute mode
    '1': {'name': 'Once a day', 'times': ['8:00']},
    '2': {'name': 'Twice a day', 'times': ['8:00', '20:00']},
    '3': {'name': 'Three times a day', 'times': ['8:00', '15:00', '20:00']},
    '4': {'name': 'Four times a day', 'times': ['8:00', '12:00', '16:00', '20:00']}
}

# Store user preferences
user_preferences = {}

# Store active message interactions
active_interactions = {}  # Format: {message_id: {user_id: action}}

async def send_quote_to_user(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Helper function to send a quote to a specific user."""
    quote_data = json.loads(get_random_quote())
    if 'error' not in quote_data:
        print('Sending quote to user')
        message = (
            f"{quote_data['content']}\n\n"
            f"*{quote_data['book']}*\n"
            f"_{quote_data['author']}_"
        )
        
        # Always show active buttons for new messages
        keyboard = [
            [
                InlineKeyboardButton("👍 Like", callback_data=f"like_{quote_data['id']}"),
                InlineKeyboardButton("👎 Dislike", callback_data=f"dislike_{quote_data['id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        sent_message = await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Initialize interaction tracking for this message
        active_interactions[sent_message.message_id] = {}

async def handle_like_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Like/Dislike button presses."""
    query = update.callback_query
    if query and query.data and query.message:
        if query.data == "disabled":
            await query.answer("You've already rated this quote!", show_alert=True)
            return
            
        # Extract action and quote_id from callback_data
        action, quote_id = query.data.split('_')
        quote_id = int(quote_id)
        user_id = query.from_user.id
        message_id = query.message.message_id
        
        # Check if user has already interacted with this specific message
        if message_id in active_interactions and user_id in active_interactions[message_id]:
            await query.answer("You've already rated this quote!", show_alert=True)
            return
        
        try:
            # Get current value and modify it
            if action == 'like':
                modify_cell(quote_id, 'value', 10)
                await query.answer("Quote liked! 👍")
            else:  # dislike
                modify_cell(quote_id, 'value', 1)
                await query.answer("Quote disliked! 👎")
            
            # Store the interaction for this specific message
            active_interactions[message_id][user_id] = action
            
            # Update the message to show disabled buttons
            keyboard = [
                [
                    InlineKeyboardButton("👍 Liked" if action == 'like' else "👎 Disliked", 
                                       callback_data="disabled")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error modifying quote value: {e}")
            await query.answer("Error updating quote value", show_alert=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if update.effective_user and update.message:
        user = update.effective_user
        keyboard = [
            [KeyboardButton("📚 Get a Random Quote")],
            [KeyboardButton("➕ Add quotes")],
            [KeyboardButton("🏆 Best_quotes")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f'Hi {user.first_name}! I will send you random quotes.\n'
            'Use /settings to configure how often you want to receive quotes.\n'
            'Or click the button below to get a random quote right now!\n'
            'To add your own quotes, click "➕ Add quotes".\n'
            'To get a PDF with the best quotes, click "🏆 Best_quotes".',
            reply_markup=reply_markup
        )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the settings conversation."""
    if update.message:
        keyboard = [[f"{k} - {v['name']}"] for k, v in PERIODS.items()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            'Please choose how often you want to receive quotes:',
            reply_markup=reply_markup
        )
    return SETTING_PERIOD

async def set_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the period selection."""
    if update.effective_user and update.message and update.message.text:
        user_id = update.effective_user.id
        choice = update.message.text[0]  # Get the first character of the choice
        
        if choice in PERIODS:
            user_preferences[user_id] = PERIODS[choice]
            # Restore the "Get a Random Quote" button
            keyboard = [[KeyboardButton("📚 Get a Random Quote")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                f'Great! You will receive quotes {PERIODS[choice]["name"].lower()}.',
                reply_markup=reply_markup
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text('Please choose a valid option.')
    return SETTING_PERIOD

async def send_quote(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a random quote to users based on their schedule."""
    current_time = f'{datetime.now().time().hour}:{datetime.now().time().minute}'
    
    for user_id, preferences in user_preferences.items():
        # If times is None, it means "every minute" mode
        if preferences['times'] is None:
            await send_quote_to_user(user_id, context)
        # Otherwise check if current time matches any of the scheduled times
        elif current_time in preferences['times']:
            await send_quote_to_user(user_id, context)

async def handle_random_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the random quote button press."""
    if update.effective_user and update.message:
        await send_quote_to_user(update.effective_user.id, context)

async def add_quotes_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler for 'Add quotes' button. Prompts user to upload a .md file."""
    if update.message:
        await update.message.reply_text(
            "Please upload a markdown (.md) file with your quotes.")
    return WAITING_MD_FILE

async def handle_md_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the uploaded .md file, parses and adds quotes to the database."""
    if update.message and update.message.document and update.effective_user:
        file = update.message.document
        if not (file.file_name and file.file_name.endswith('.md')):
            await update.message.reply_text("File must have a .md extension. Please try again.")
            return WAITING_MD_FILE
        # Download file
        file_path = os.path.join("app", f"user_{update.effective_user.id}_{file.file_name}")
        new_file = await file.get_file()
        await new_file.download_to_drive(file_path)
        try:
            book_quotes = parse_md_to_quotes(file_path)
            db_fill_in(book_quotes)
            count = len(book_quotes.content)
            await update.message.reply_text(f"Successfully added {count} quotes from '{book_quotes.book}' by {book_quotes.author}.")
        except Exception as e:
            await update.message.reply_text(f"Error processing file: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
        return ConversationHandler.END
    else:
        if update.message:
            await update.message.reply_text("Please upload a markdown (.md) file.")
        return WAITING_MD_FILE

async def handle_best_quotes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерирует PDF с лучшими цитатами и отправляет пользователю."""
    if update.message:
        await update.message.reply_text("Генерирую PDF с лучшими цитатами...")
        pdf_path = make_pdf("best_quotes.pdf")
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                await update.message.reply_document(pdf_file, filename="best_quotes.pdf")
        else:
            await update.message.reply_text("Не удалось создать PDF-файл. Возможно, нет лучших цитат.")

def main() -> None:
    """Start the bot."""
    # Get token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

    # Create the Application
    application = Application.builder().token(token).build()

    # Add conversation handler for settings
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('settings', settings),
            MessageHandler(filters.Regex('^➕ Add quotes$'), add_quotes_entry),
            MessageHandler(filters.Regex('^🏆 Best_quotes$'), handle_best_quotes)
        ],
        states={
            SETTING_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_period)],
            WAITING_MD_FILE: [MessageHandler(filters.Document.ALL, handle_md_file)]
        },
        fallbacks=[],
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Regex('^📚 Get a Random Quote$'), handle_random_quote))
    application.add_handler(CallbackQueryHandler(handle_like_dislike, pattern='^(like|dislike|disabled)'))

    # Add job for sending quotes
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(send_quote, interval=60)  # Check every minute

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


