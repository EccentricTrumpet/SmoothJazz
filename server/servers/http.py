from flask import Flask, render_template
from flask.views import MethodView
from flask_cors import CORS
from services.game_service import GameService


class HelloAPI(MethodView):
    init_every_request = False

    def get(self):
        return "Hello, World!"


class HomeAPI(MethodView):
    init_every_request = False

    def get(self):
        return render_template("index.html")


class GameAPI(MethodView):
    init_every_request = False

    def __init__(self, game_service: GameService):
        self.__game_service: GameService = game_service

    def post(self):
        return self.__game_service.create_game()


class HttpServer:
    def __init__(self, game_service: GameService, static_path: str) -> None:
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
            "/game", view_func=GameAPI.as_view("game-api", game_service)
        )
