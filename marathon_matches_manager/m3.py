"""
Overview:
    todo

Usage:
  m3 new <name>
  m3 vis
  m3 hi

Options:
  -h, --help                        : show this help message
      --name=<name>                 : [default: general]
"""

import logging

from docopt import docopt
from flask import Flask, render_template

from .generate_template import generate_template

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]: %(message)s")


@app.route('/')
def index():
    return render_template('index.html')


def main():
    args = docopt(__doc__)
    print(args)
    if args['new']:
        generate_template(args['<name>'])
    elif args['vis']:
        app.run(host='0.0.0.0', port=5000)
    elif args['hi']:
        print("hello!")


if __name__ == "__main__":
    main()
