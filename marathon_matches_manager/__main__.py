"""
Overview:
    todo

Usage:
  m3 new  <name> [-p | --pure]  [-v | --verbose] [--no-info]
  m3 init <name> [-p | --pure]  [-v | --verbose] [--no-info]
  m3 info [--path=<path>]
  m3 official-tools setup
  m3 test gen [--name=<name>] [--num=<gen-num>] [--seed=<seed>] [--over-write]
  m3 test run [--name=<name>] [--concurrency=<concurrency>]
  m3 server run [--dev]
  m3 submit local
  m3 submit server
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
import subprocess
from typing import Union

from docopt import docopt
from fastapi import FastAPI

from .lib.environment import environment
from .lib.models.config import ProjectConfig
from .lib.new import generate_template
from .lib.official_tools import setup_official_tools
from .lib.testcases import generate_testcases

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[ProjectConfig, None] = None):
    return {"item_id": item_id, "q": q}


def main():
    if environment.in_project:
        os.environ["PROJECT_ROOT_PATH"] = str(environment.project_root_path)

    args = docopt(__doc__)

    log_level = logging.DEBUG if args["--verbose"] else logging.WARNING if args["--no-info"] else logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s]: %(message)s")

    logger = logging.getLogger(__name__)
    # logger.debug(args)

    if args["new"]:
        generate_template(args["<name>"])
    elif args["test"]:
        generate_testcases()
    # elif args["vis"]:
    # app.run(host="0.0.0.0", port=5000)
    elif args["official-tools"]:
        if args["setup"]:
            setup_official_tools(environment.project_config)
    elif args["hi"]:
        print("hello!")
    elif args["server"]:
        subprocess.run(f"uvicorn marathon_matches_manager.__main__:app {'--reload' if args['--dev'] else ''}".split())


if __name__ == "__main__":
    main()
