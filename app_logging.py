import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)  # Capture all log levels, including DEBUG

file_handler = logging.FileHandler('app.log')
console_handler = logging.StreamHandler()

file_handler.setLevel(logging.DEBUG)  # Capture all log levels, including DEBUG
console_handler.setLevel(logging.DEBUG)  # Capture all log levels, including DEBUG

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
