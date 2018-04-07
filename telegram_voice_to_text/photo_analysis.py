from PIL import Image  # Importando o módulo Pillow para abrir a imagem no script
import pytesseract  # Módulo para a utilização da tecnologia OCR
import requests
from speech_to_text import process_text


def photo_analysis(bot, update):
    print(update.message.document)
    file = update.message.document.get_file(timeout=120)

    response = requests.get(file['file_path'], stream=True)
    response.raise_for_status()

    with open('output.jpg', 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    with open('output.jpg', 'r') as handle:
        text = pytesseract.image_to_string(Image.open(handle))
        update.message.reply_text(u"Transcrição do texto da imagem: " + text)

    classification = process_text(text)
    update.message.reply_text(u"bin_score: " + unicode(classification[0]))
    update.message.reply_text(u"cat_dict : " + unicode(classification[1]))


def main():
    # ...
    dp.add_handler(MessageHandler(Filters.document, photo_analysis))
    # ...
