import argparse
import logging
import os.path as PATH
from servers.http import HttpServer
from servers.socket import initialize
from services.match import MatchService

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
        format="%(asctime)s [%(levelname)s] {%(filename)s:%(lineno)d}: %(message)s",
    )

    # Initialize services
    match_service = MatchService()

    # Initialize servers
    http = HttpServer(
        match_service, PATH.join(PATH.dirname(PATH.abspath(__file__)), "build")
    )
    socketio = initialize(http.app, match_service)

    # Start servers
    socketio.run(http.app, host="0.0.0.0", port=5001)