import multiprocessing
from gunicorn.app.base import BaseApplication
from app import app  # Make sure app.py is in the same directory and defines `app = Flask(__name__)`

class GunicornApp(BaseApplication):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    options = {
        "bind": "0.0.0.0:8000",
        "workers": 1,
        "threads": 2,
        "worker_class": "gthread",
        "timeout": 300,
        "loglevel": "info",
    }

    GunicornApp(app, options).run()
