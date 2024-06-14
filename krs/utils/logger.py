import logging
from logging.handlers import TimedRotatingFileHandler

# Configure the handler
handler = TimedRotatingFileHandler(filename='my_app.log', when='midnight', interval=1)

# Set logging level and format
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(handler)


