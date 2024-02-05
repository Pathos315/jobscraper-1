import logging
import logging.config
import json
from pathlib import Path
from src.configs import CONFIG


logger = logging.getLogger("jobscraper")

logging_configs = Path(CONFIG.logging_file_path).resolve()
with open(logging_configs) as f_in:
    log_config = json.load(f_in)
logging.config.dictConfig(log_config)
