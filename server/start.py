import argparse
import logging
import os.path as PATH
from servers.http import HttpServer
from servers.socket import initialize
from services.game_service import GameService

if __name__ == "__main__":
    # Server configuration
    parser = argparse.ArgumentParser(description="Configuration for server.")
    parser.add_argument(
        "--debug",
        metavar="d",
        type=bool,
        default=False,
        required=False,
        help="If set, print detailed debug logging.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(threadName)s] {%(filename)s:%(lineno)d}: %(message)s",
    )

    # Initialize services
    game_service = GameService()

    # Initialize servers
    http = HttpServer(
        game_service, PATH.join(PATH.dirname(PATH.abspath(__file__)), "build")
    )
    socketio = initialize(http.app)

    # Start servers
    socketio.run(http.app, host="0.0.0.0", port=5001)
