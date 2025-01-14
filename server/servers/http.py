from flask import Flask, abort, request
from flask.views import MethodView
from flask_cors import CORS
from services.match import MatchService


class MatchPost(MethodView):
    init_every_request = False

    def __init__(self, match_service: MatchService) -> None:
        self.__match_service = match_service

    def post(self):
        debug = bool(request.json["debug"])
        return self.__match_service.create(debug).json()


class MatchGet(MethodView):
    init_every_request = False

    def __init__(self, match_service: MatchService) -> None:
        self.__match_service = match_service

    def get(self, id: int):
        if (response := self.__match_service.get(id)) is None:
            abort(404)
        else:
            return (
                response.json(),
                200,
                {
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "Cache-Control": "public, max-age=0",
                },
            )


def init_http(service: MatchService, static_path: str) -> Flask:
    app = Flask(__name__, static_url_path="", static_folder=static_path)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Match APIs
    app.add_url_rule("/match", view_func=MatchPost.as_view("matchPost", service))
    app.add_url_rule("/match/<int:id>", view_func=MatchGet.as_view("matchGet", service))

    # Redirect all other routes to index.html (React app)
    app.register_error_handler(404, lambda e: app.send_static_file("index.html"))

    return app
