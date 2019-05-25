from api import create_app
import os

app = create_app()
PORT = os.environ.get('port', 5000)
HOST = os.environ.get('host', '127.0.0.1')

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
