from app.cli import start
from app.logging.setup_logging import setup_logging

if __name__ == "__main__":
    setup_logging()
    start()
