import logging

from scrape.dir import change_dir

logger = logging.getLogger("jobscraper")
logger.setLevel(level=logging.INFO)
DATEFMT = "%d-%b-%y %H:%M:%S"
formatter = logging.Formatter("[jobscraper]: %(asctime)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

FILENAME = "jobscraper_printedlogs"

with change_dir(FILENAME):
    doc_handler = logging.FileHandler(FILENAME)
    doc_handler.setFormatter(formatter)
    logger.addHandler(doc_handler)
