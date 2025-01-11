import logging
import os.path as PATH
from argparse import ArgumentParser
from os import environ as ENV

from servers.http import init_http
from servers.socket import init_sockets
from services.match import MatchService

if __name__ == "__main__":
    # Server configuration
    parser = ArgumentParser(description="Configuration for server.")
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
    http = init_http(
        match_service, PATH.join(PATH.dirname(PATH.abspath(__file__)), "build")
    )

    socketio = init_sockets(http, match_service)

    # Start servers
    socketio.run(
        http, host="0.0.0.0", port=ENV.get("PORT", 5001), allow_unsafe_werkzeug=True
    )
