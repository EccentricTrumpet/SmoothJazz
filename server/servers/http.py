import logging
from flask import Flask, render_template, request
from flask.views import MethodView
from flask_cors import CORS
from services.match_service import MatchService


class HelloAPI(MethodView):
    init_every_request = False

    def get(self):
        return "Hello, World!"


class HomeAPI(MethodView):
    init_every_request = False

    def get(self):
        return render_template("index.html")


class MatchAPI(MethodView):
    init_every_request = False

    def __init__(self, match_service: MatchService):
        self.__match_service: MatchService = match_service

    def post(self):
        creator = request.json["name"]
        speed = int(request.json["speed"])
        debug = bool(request.json["debug"])

        logging.info(
            f"Creating new match - creator: {creator}, speed: {speed}, debug: {debug}"
        )

        return self.__match_service.create_match(creator, 0.5 / speed, debug)


class HttpServer:
    def __init__(self, match_service: MatchService, static_path: str) -> None:
        self.app = Flask(
            __name__,
            static_url_path="",
            static_folder=static_path,
            template_folder=static_path,
        )
        CORS(self.app, resources={r"/*": {"origins": "*"}})

        self.app.add_url_rule("/", view_func=HomeAPI.as_view("home-api"))
        self.app.add_url_rule("/hello", view_func=HelloAPI.as_view("hello-api"))
        self.app.add_url_rule(
            "/match", view_func=MatchAPI.as_view("match-api", match_service)
        )
