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
import logging
import operator
import os
import ssl
import sys
import time


############################ CONSTANTS ###############################
PORT = 443
# CA_CERT_FILE = "/etc/ssl/certs/chained.pem"
# PRIVATE_KEY_FILE = "/etc/ssl/private/domain.key"
CA_CERT_FILE = "/etc/letsencrypt/live/tabletenniser.ddns.net/fullchain.pem"
PRIVATE_KEY_FILE = "/etc/letsencrypt/live/tabletenniser.ddns.net/privkey.pem"
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
@view('error')
def error_page(error):
  return {}


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

if __name__ == "__main__":
  logging.basicConfig(
          # stream=sys.stdout, level=logging.DEBUG,
          filename='main.log', filemode='w', level=logging.DEBUG,
          format='%(asctime)s %(levelname)s %(module)s.py:%(lineno)s: %(message)s',
          datefmt='%m-%d %H:%M:%S')
  app = SessionMiddleware(default_app(), session_opts)
  run(app=app, host="0.0.0.0", port=443, server=SSLCherryPyServer, debug=True)
  # run(app=app, host='0.0.0.0', port=PORT, debug=True)
