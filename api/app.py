from flask_cors import CORS

from . import create_app



if __name__ == '__main__':
    app = create_app()
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
