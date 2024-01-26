import logging
import logging.config
from src.configs import LOGGING_CONFIG

logger = logging.getLogger("jobscraper")
logging.config.dictConfig(LOGGING_CONFIG)
