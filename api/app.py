from api import create_app
import os

app = create_app()
PORT = os.environ.get('PORT', 5005)
HOST = os.environ.get('HOST', '127.0.0.1')

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
