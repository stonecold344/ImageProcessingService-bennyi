import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)
        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    @staticmethod
    def is_current_msg_photo(msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        print(f'Incoming message: {msg}')  # Print incoming message for debugging

        chat_id = msg['chat']['id']
        self.send_text(chat_id, f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        # Check if the message has text
        if 'text' in msg:
            text = msg['text']
            self.send_text_with_quote(msg['chat']['id'], text, quoted_msg_id=msg['message_id'])
        else:
            # Check if the message has caption
            if 'caption' in msg:
                caption = msg['caption']
                self.send_text_with_quote(msg['chat']['id'], caption, quoted_msg_id=msg['message_id'])
            else:
                logger.warning('Received a message without text or caption.')


class ImageProcessingBot(Bot):

    def greet_user(self, chat_id):
        self.send_text(chat_id, "Welcome to ImageProcessingBot! Send me a photo with a caption to apply filters.")

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        chat_id = msg['chat']['id']

        try:
            if 'text' in msg:
                if msg['text'].lower() == '/start':
                    self.greet_user(chat_id)
                else:
                    self.send_text(chat_id, "Send me a photo with a caption to apply filters.")
            elif 'caption' in msg:
                caption = msg['caption'].lower()
                img_path = self.download_user_photo(msg)
                img = Img(img_path)

                if 'blur' in caption:
                    img.blur()
                elif 'contour' in caption:
                    img.contour()
                elif 'rotate' in caption:
                    img.rotate()
                elif 'counter' in caption:
                    img.counter_rotate()
                elif 'segment' in caption:
                    img.segment()
                elif 'salt and pepper' in caption:
                    img.salt_n_pepper()
                else:
                    self.send_text(chat_id, "Invalid filter.")
                    return

                filtered_img_path = img.save_img()
                self.send_photo(chat_id, filtered_img_path)
            else:
                self.send_text(chat_id, 'Please provide a caption for image processing.')
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.send_text(chat_id, "Something went wrong... please try again.")





