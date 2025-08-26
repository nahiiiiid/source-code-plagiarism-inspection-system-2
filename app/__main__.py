import sys
import os

sys.path.append(os.path.dirname(__file__))  # Adds current folder to Python path
from web import create_app


from .web import create_app
app = create_app()

if __name__ == '__main__':
    app.run()
