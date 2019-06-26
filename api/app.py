from flask_cors import CORS

from api import create_app
import os

app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

PORT = os.environ.get('PORT', 5000)
HOST = os.environ.get('HOST', '127.0.0.1')
# HOST = '0.0.0.0'
#
if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
