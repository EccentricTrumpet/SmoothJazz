import argparse
import logging
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(
    __name__, static_url_path="", static_folder="build", template_folder="build"
)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=False)


@app.route("/hello")
def hello():
    return "Hello, World!"


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("connect")
def connected():
    """event listener when client connects to the server"""
    logging.info(f"client {request.sid} has connected")


@socketio.on("data")
def handle_message(data):
    """event listener when client types a message"""
    logging.info(f"client {request.sid} sent data: {str(data)}")
    emit("data", {"data": data, "id": request.sid}, broadcast=True)


@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    logging.info(f"client {request.sid} has disconnected")


if __name__ == "__main__":
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

    socketio.run(app, host="0.0.0.0")
