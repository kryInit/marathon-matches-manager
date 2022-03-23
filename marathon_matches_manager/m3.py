"""
Overview:
    todo

Usage:
  m3 info [--path=<path>]
  m3 new <name> [-p | --pure]  [-v | --verbose] [--no-info]
  m3 test gen [--name=<name>] [--num=<gen-num>] [--seed=<seed>] [--over-write]
  m3 test run [--name=<name>] [--concurrency=<concurrency>]
  m3 submit server
  m3 submit local
  m3 optimize
  m3 stat
  m3 log
  m3 vis [-v | --verbose] [--no-info]
  m3 hi [-v | --verbose] [--no-info]
  m3 -h | --help

Options:
  -h, --help           : show this help message
  -p, --pure           : no related contest
  -v, --verbose        : output debug and more important log
      --no-info        : output more important log than info
      --name=<name>    : [default: general]
"""

import logging

from docopt import docopt
from flask import Flask, render_template

from marathon_matches_manager.new.generate_template import generate_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def main():
    args = docopt(__doc__)

    log_level = logging.DEBUG if args["--verbose"] else logging.WARNING if args["--no-info"] else logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s]: %(message)s")

    logger = logging.getLogger(__name__)
    # logger.debug(args)

    if args["new"]:
        generate_template(args["<name>"])
    elif args["vis"]:
        app.run(host="0.0.0.0", port=5000)
    elif args["hi"]:
        print("hello!")


if __name__ == "__main__":
    main()
