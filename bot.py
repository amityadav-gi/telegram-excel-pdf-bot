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

    try:

        document = update.message.document

        print("Received file:", document.file_name)

        if not document.file_name.endswith((".xlsx", ".xls")):
            await update.message.reply_text("Please send Excel file only.")
            return

        file = await context.bot.get_file(document.file_id)

        input_path = os.path.join(DOWNLOAD_DIR, document.file_name)

        await file.download_to_drive(input_path)

        print("Downloaded:", input_path)

        await update.message.reply_text("Converting to PDF...")

        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                OUTPUT_DIR,
                input_path
            ],
            capture_output=True,
            text=True
        )

        print("LibreOffice stdout:", result.stdout)
        print("LibreOffice stderr:", result.stderr)

        pdf_name = os.path.splitext(document.file_name)[0] + ".pdf"
        pdf_path = os.path.join(OUTPUT_DIR, pdf_name)

        print("Looking for PDF:", pdf_path)

        if os.path.exists(pdf_path):

            print("PDF created successfully")

            await update.message.reply_document(
                document=open(pdf_path, "rb")
            )

            os.remove(pdf_path)
            os.remove(input_path)

        else:

            print("PDF NOT created")

            await update.message.reply_text(
                "Conversion failed."
            )

    except Exception as e:

        print("ERROR:", str(e))

        await update.message.reply_text(
            f"Error: {str(e)}"
        )


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.Document.ALL, handle_file)
    )

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()
