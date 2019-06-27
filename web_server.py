from web.app import app
from config import host

if __name__ == "__main__":
    app.run(host=host, debug=True)
