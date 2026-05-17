import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = "downloads"
OUTPUT_DIR = "output"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document.file_name.endswith((".xlsx", ".xls")):
        await update.message.reply_text("Please send Excel file.")
        return

    file = await context.bot.get_file(document.file_id)

    input_path = os.path.join(DOWNLOAD_DIR, document.file_name)

    await file.download_to_drive(input_path)

    await update.message.reply_text("Converting to PDF...")

    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        OUTPUT_DIR,
        input_path
    ])

    pdf_name = os.path.splitext(document.file_name)[0] + ".pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_name)

    if os.path.exists(pdf_path):

        await update.message.reply_document(
            document=open(pdf_path, "rb")
        )

        os.remove(pdf_path)
        os.remove(input_path)

    else:
        await update.message.reply_text("Conversion failed.")


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.Document.ALL, handle_file)
    )

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()
