import cProfile
import logging
logging.basicConfig(level=logging.WARNING)

from src.engine import create_app

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    app = create_app("development")
    app.MainLoop()

    profiler.disable()
    profiler.print_stats(sort="cumulative")
