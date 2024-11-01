import logging
import os
from io import BytesIO
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from fpdf import FPDF
import tempfile
import requests

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the PDF creation function
def create_pdf(image_path, layout):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=0.5)

    # A4 dimensions in mm with 0.5cm margins (5mm)
    page_width = 210 - 10  # 210mm width - 5mm left - 5mm right
    page_height = 297 - 10  # 297mm height - 5mm top - 5mm bottom

    if layout == 2:
        img_width = page_width / 2
        img_height = page_height
        pdf.image(image_path, x=5, y=5, w=img_width, h=img_height)
        pdf.image(image_path, x=img_width + 5, y=5, w=img_width, h=img_height)
    elif layout == 4:
        img_width = page_width / 2
        img_height = page_height / 2
        for i in range(2):
            for j in range(2):
                pdf.image(image_path, x=j * img_width + 5, y=i * img_height + 5, w=img_width, h=img_height)

    pdf.output("file.pdf", 'F')

async def send_layout_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("2 Images", callback_data='2'),
            InlineKeyboardButton("4 Images", callback_data='4')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose the layout option:", reply_markup=reply_markup)

# Handle /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an image, then specify the layout: 2 or 4.")

# Handle image messages
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Image received from %s", user.first_name)

    photo = update.message.photo[-1].file_id

    recieved_file =await context.bot.get_file(photo)
    path = recieved_file.file_path

    # Download the image file
    image_file =requests.get(path).content
    with open('image.jpg', 'wb') as f:
        f.write(image_file)

    await send_layout_options(update, context)

# Handle layout option selection
async def handle_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    layout = int(query.data)  # This will be 2 or 4

    if os.path.isfile("image.jpg"):
    
        create_pdf("image.jpg",int(layout))

        # Send the PDF file to the user
        await context.bot.send_document(chat_id=query.message.chat_id, document=open('file.pdf', 'rb'))

        # Clean up the temporary files
       # os.remove('image.jpg')
        os.remove('file.pdf')
    else:
        await update.message.reply_text("No image found. Please send an image first.")    

# Main function to run the bot
def main():
    application = ApplicationBuilder().token("7268905650:AAEE02n3JCEXdE4pf19kWhQ3F_KeZi-ZQHo").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CallbackQueryHandler(handle_layout))

    application.run_polling()

if __name__ == '__main__':
    main()
import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from fpdf import FPDF

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define PDF creation function
def create_pdf(image_path, layout):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=0.5)

    # A4 dimensions in mm with 0.5cm margins (5mm)
    page_width = 210 - 10
    page_height = 297 - 10

    img_width = page_width / (2 if layout == 2 else 1)
    img_height = page_height / (2 if layout == 4 else 1)

    for i in range((layout + 1) // 2):
        for j in range(2):
            if (i * 2 + j) < layout:
                pdf.image(image_path, x=j * img_width + 5, y=i * img_height + 5, w=img_width, h=img_height)

    pdf.output("file.pdf", 'F')

async def send_layout_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("2 Images", callback_data='2'),
         InlineKeyboardButton("4 Images", callback_data='4')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose the layout option:", reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an image, then specify the layout: 2 or 4.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Image received from %s", user.first_name)

    photo = update.message.photo[-1].file_id
    received_file = await context.bot.get_file(photo)
    image_path = 'image.jpg'
    
    # Download the image
    image_file = requests.get(received_file.file_path).content
    with open(image_path, 'wb') as f:
        f.write(image_file)

    await send_layout_options(update, context)

async def handle_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    layout = int(query.data)
    image_path = "image.jpg"

    if os.path.isfile(image_path):
        create_pdf(image_path, layout)
        await context.bot.send_document(chat_id=query.message.chat_id, document=open('file.pdf', 'rb'))
        os.remove(image_path)
        os.remove('file.pdf')
    else:
        await query.message.reply_text("No image found. Please send an image first.")

def main():
    import os
    TOKEN = os.getenv('BOTAPIKEY')
    PORT = int(os.environ.get('PORT', '4000'))
    URL = os.getenv('URL')
    HOOK_URL = URL + '/' + TOKEN
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CallbackQueryHandler(handle_layout))

    application.run_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN, webhook_url=HOOK_URL)

if __name__ == '__main__':
    main()
