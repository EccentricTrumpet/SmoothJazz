from flask import Flask, abort, render_template, request
from flask.views import MethodView
from flask_cors import CORS
from services.match import MatchService


class HomeAPI(MethodView):
    init_every_request = False

    def get(self):
        return render_template("index.html")


class MatchPostAPI(MethodView):
    init_every_request = False

    def __init__(self, match_service: MatchService):
        self.__match_service = match_service

    def post(self):
        debug = bool(request.json["debug"])
        return self.__match_service.create(debug).json()


class MatchGetAPI(MethodView):
    init_every_request = False

    def __init__(self, match_service: MatchService):
        self.__match_service = match_service

    def get(self, id: int):
        response = self.__match_service.get(id)
        if response is None:
            abort(404)
        else:
            return response.json()


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
        self.app.add_url_rule(
            "/match", view_func=MatchPostAPI.as_view("match-post-api", match_service)
        )
        self.app.add_url_rule(
            "/match/<int:id>",
            view_func=MatchGetAPI.as_view("match-get-api", match_service),
        )
