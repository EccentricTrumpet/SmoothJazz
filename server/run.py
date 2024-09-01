import argparse
from flask import Flask, render_template
import logging

app = Flask(__name__, static_url_path='',
                  static_folder='build',
                  template_folder='build')

@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configuration for server.')
    parser.add_argument('--debug', metavar='d', type=bool, default=False, required=False,
                        help='If set, print detailed debug logging.')
    args = parser.parse_args()

    logging.basicConfig(level = logging.DEBUG if args.debug else logging.INFO,
            format='%(asctime)s [%(levelname)s] [%(threadName)s] {%(filename)s:%(lineno)d}: %(message)s')

    app.run(host="0.0.0.0")