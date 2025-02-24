import logging

file_log = logging.FileHandler("logfile.log")
console_out = logging.StreamHandler()

logging.basicConfig(
    handlers=(file_log, console_out),
    format="[%(asctime)s | %(levelname)s]: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)

print("logger name:", __name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# level=logger.INFO

logger.info(" >>> ---- Module reimported! ---- <<< ")

# wow
print("logger name:", __name__)
