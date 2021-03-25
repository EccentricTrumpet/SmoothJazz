# -*- coding: utf-8 -*-# To run: sudo /usr/local/bin/python3.7 main.py

from beaker.middleware import SessionMiddleware
from bottle import route, run, get, post, request, static_file, redirect, error, view, response, ServerAdapter, default_app
from cheroot import wsgi
from cheroot.ssl.builtin import BuiltinSSLAdapter
from googleapiclient.discovery import build
from oauth2client import client
import bottle
import httplib2
import json
import random
import logging
import operator
import os
import ssl
import sys
import time


############################ CONSTANTS ###############################
PORT = 8080
# CA_CERT_FILE = "/etc/ssl/certs/chained.pem"
# PRIVATE_KEY_FILE = "/etc/ssl/private/domain.key"
# CA_CERT_FILE = "/etc/letsencrypt/live/tabletenniser.ddns.net/fullchain.pem"
# PRIVATE_KEY_FILE = "/etc/letsencrypt/live/tabletenniser.ddns.net/privkey.pem"
CUR_FOLDER = os.getcwd()

######################## GLOBAL SETTINGS #############################
bottle.debug(True)

# define beaker options
# -Each session data is stored inside memory
# -The cookie expires at the end of the browser session
# -The session will save itself when accessed during a request
#  so save() method doesn't need to be called
session_opts = {
  'session.type': 'memory',
  'session.cookie_expires': 900,
  'session.auto': True,
  'session.secret': 'sdfasdasdfd',
  # 'session.secure': True
}

############################ WEBPAGES ###############################
def restricted_page(func):
  def wrapper(*args, **kargs):
    beaker_session = request.environ.get('beaker.session')
    if 'email' not in beaker_session:
      logging.info("redirect to sign_in page!")
      return bottle.redirect("/sign_in")
    return func(*args, **kargs)
  return wrapper

@route('/img/<filename>')
@restricted_page
def display(filename):
  return static_file(filename, root='img/')

@route('/pdf/<filename>')
@restricted_page
def display(filename):
  return static_file(filename, root='pdf/')

@route('/css/<filename>')
def display(filename):
  return static_file(filename, root='css/')

@route('/js/<filename>')
def display(filename):
  return static_file(filename, root='js/')

@get('/redirect')
def redirect_page():
  logging.info('Reach /redirect')
  beaker_session = request.environ.get('beaker.session')
  code = request.query.get('code', '')
  with open('client_secrets.json') as client_secret_file:
    client_secret = json.load(client_secret_file)
    flow = client.OAuth2WebServerFlow(
      client_id = client_secret['web']['client_id'],
      client_secret = client_secret['web']['client_secret'],
      scope = 'https://www.googleapis.com/auth/userinfo.email',
      redirect_uri = 'https://tabletenniser.ddns.net:{}/redirect'.format(PORT))
    credentials = flow.step2_exchange(code)

    token = credentials.id_token['sub']
    http = credentials.authorize(httplib2.Http())

    user_service = build('oauth2', 'v2', http = http, cache_discovery=False)
    user_document = user_service.userinfo().get().execute()
    beaker_session['email'] = user_document['email']
    beaker_session.save()
    logging.debug("Session: %s; Code: %s; Token: %s", beaker_session, code, token)
  return bottle.redirect('/')

@route('/sign_in')
def display():
  flow = client.flow_from_clientsecrets(
    'client_secrets.json',
    scope='https://www.googleapis.com/auth/userinfo.email',
    redirect_uri = 'https://tabletenniser.ddns.net:{}/redirect'.format(PORT))
  logging.debug('Client ID: %s; Client Secret: %s; Redirect URI: %s',
          flow.client_id, flow.client_secret, flow.redirect_uri)
  auth_uri = flow.step1_get_authorize_url()
  logging.info('Redirecting to %s', auth_uri)
  return bottle.redirect(auth_uri)

@view('invalid_cred')
def display():
  return "Sorry, you do not have access to the web content!"

@error(404)
@error(500)
#@view('error')
def error_page(error):
  return {}

@route('/')
def display():
    return DealCards([1, 2, 3, 4])

@route('/create_game')
def display():
  player_id = request.query.playerid
  db = SingletonDBInstance()
  return "Created game " + str(db.CreateGame(player_id))

@route('/add_player')
def display():
  player_id = request.query.playerid
  game_id = request.query.gameid
  db = SingletonDBInstance()
  return "Updated game " + str(db.AddPlayer(game_id, player_id))

@route('/start_game')
def display():
  player_id = request.query.playerid
  game_id = request.query.gameid
  db = SingletonDBInstance()
  return "Started game " + str(db.StartGame(game_id, player_id))

@route('/get_game')
def display():
  player_id = request.query.playerid
  game_id = request.query.gameid
  db = SingletonDBInstance()
  return "Game " + str(db.GetGame(game_id, player_id))

class SSLCherryPyServer(ServerAdapter):
  def run(self, handler):
    server = wsgi.Server((self.host, self.port), handler)
    server.ssl_adapter = BuiltinSSLAdapter(CA_CERT_FILE, PRIVATE_KEY_FILE)

    # Disable old negotiation protocols to only allow TLSv1.2 for security
    server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1
    server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1_1

    try:
      server.start()
    finally:
      server.stop()

# 52 is small joker, 53 is the big joker
# 0 - 12 HEARTS
# 13 - 25 CLUBS
# 26 - 38 DIAMONDS
# 39 - 51 SPADES
def GetSuite(index):
    if index == 52:
        return "joker"
    if index == 53:
        return "JOKER"

    card = ""
    if index % 13 == 0:
        card = "King"
    elif index % 13 == 1:
        card = "Ace"
    elif index % 13 == 11:
        card = "Jack"
    elif index % 13 == 12:
        card = "Queen"
    else:
        card = str(index % 13)
    card += "_"
    
    if int(index / 13) == 0:
        card += "Hearts"
    elif int(index / 13) == 1:
        card += "Clubs"
    elif int(index / 13) == 2:
        card += "Diamonds"
    elif int(index / 13) == 3:
        card += "Spades"
    return card

def DealCards(player_ids):
    if len(player_ids) != 4:
        raise RuntimeError("Must have exactly 4 players")
    # shuffle two decks of cards
    cards = [GetSuite(x) for x in range(54)] + [GetSuite(x) for x in range(54)]
    random.shuffle(cards)

    result = dict()

    for player in player_ids:
        result[player] = cards[:26]
        del cards[:26]
    return result


# In-memory fake db
class SingletonDBInstance:
    instance = None
    games = None
    next_game_id = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(SingletonDBInstance, cls).__new__(cls)
            cls.games = dict()
            cls.next_game_id = 0
        return cls.instance

    @classmethod
    def CreateGame(cls, player_id):
        print(cls.games)
        game_id = str(cls.next_game_id)
        cls.games[game_id] = dict()
        cls.games[game_id]["state"] = "NOT_READY"
        cls.games[game_id]["creator"] = player_id
        cls.games[game_id]["players"] = [player_id]
        cls.next_game_id += 1
        return cls.next_game_id - 1

    """
    """
    @classmethod
    def AddPlayer(cls, game_id, player_id):
        print(cls.games)
        if game_id not in cls.games.keys():
            raise RuntimeError("Game does not exist")
        if len(cls.games[game_id]["players"]) >= 4:
            raise RuntimeError("Game already has enough players")
        if player_id in cls.games[game_id]["players"]:
            raise RuntimeError("Already added player")
        cls.games[game_id]["players"].append(player_id)
        if len(cls.games[game_id]["players"]) == 4:
            cls.games[game_id]["state"] = "READY_TO_START"
        return cls.games[game_id]


    """
    """
    @classmethod
    def StartGame(cls, game_id, player_id):
        print(cls.games)
        if game_id not in cls.games.keys():
            raise RuntimeError("Game does not exist")
        if len(cls.games[game_id]["players"]) < 4:
            raise RuntimeError("Game does not have enough players")
        if cls.games[game_id]["creator"] != player_id:
            raise RuntimeError("Only creater can start the game")

        # Update game state
        cls.games[game_id]["state"] = "WAITING_FOR_PLAYER_" + player_id;

        # Deal cards
        cls.games[game_id]["allcards"] = DealCards(cls.games[game_id]["players"])

        # Player cards 
        cls.games[game_id]["cards"] = cls.games[game_id]["allcards"][player_id]

        # Deal cards
        cls.games[game_id]["lastplayedcards"] = []

        return cls.games[game_id]

    @classmethod
    def GetGame(cls, game_id, player_id):
        print(cls.games)

        # Update player cards 
        cls.games[game_id]["cards"] = cls.games[game_id]["allcards"][player_id]

        return cls.games[game_id]


if __name__ == "__main__":
  logging.basicConfig(
          # stream=sys.stdout, level=logging.DEBUG,
          filename='main.log', filemode='w', level=logging.DEBUG,
          format='%(asctime)s %(levelname)s %(module)s.py:%(lineno)s: %(message)s',
          datefmt='%m-%d %H:%M:%S')
  app = SessionMiddleware(default_app(), session_opts)
  # run(app=app, host="0.0.0.0", port=443, server=SSLCherryPyServer, debug=True)
  run(app=app, host='localhost', port=PORT, debug=True)
