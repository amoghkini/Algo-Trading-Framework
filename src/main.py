from app.app import create_app
from config.config import get_server_config

app = create_app()

server_config = get_server_config()
port = server_config.get('port')

if __name__ == "__main__":
    app.run(debug=True, port=port)
