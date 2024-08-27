import logging
logging.basicConfig(level=logging.WARNING)

from src.engine import create_app

if __name__ == "__main__":
    app = create_app()
    app.MainLoop()
