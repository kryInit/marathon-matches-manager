"""
Overview:
    todo

Usage:
  m3 new  <name> [-p | --pure]  [-v | --verbose] [--no-info]
  m3 init <name> [-p | --pure]  [-v | --verbose] [--no-info]
  m3 info [--path <path>]
  m3 run <command-name>
  m3 gen suite [--name <name>] [--case-num <case-num>] [--seed <seed>]
  m3 test suite [--name <name>] [--case-num <case-num>] [--concurrency <concurrency>]
  m3 test case <name>
  m3 utils gen-seeds [-n <n>] [--seed <seed>] [--upper-bound <upper-bound>] [-v | --verbose] [--no-info]
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
      --name=<name>    : [default: main]
  -n                   : [default: 100]
"""
import logzero

# ここで設定するのがいいのかはよくわからん（全てに適用されて欲しい気持ちはありつつ、変えたくなる時は来るのかもしれない）
formatter = logzero.LogFormatter(
    fmt="%(color)s[%(levelname)7s %(asctime)s]%(end_color)s %(message)s",
    datefmt="%m/%d %H:%M:%S",
)
logzero.setup_default_logger(formatter=formatter)

import subprocess
from typing import Union

from docopt import docopt
from fastapi import FastAPI

from marathon_matches_manager.lib.test_solver.case_generator import TestSuiteGenerator

from .lib.misc import environment
from .lib.models.config import ProjectConfig
from .lib.new import generate_template
from .lib.run import exec_command_by_name
from .lib.test_solver import TestRunner
from .lib.utils import gen_seeds

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[ProjectConfig, None] = None):
    return {"item_id": item_id, "q": q}


def main():
    args = docopt(__doc__)

    logzero.loglevel(logzero.DEBUG)
    # logzero.loglevel(logzero.DEBUG if args["--verbose"] else logzero.WARNING if args["--no-info"] else logzero.INFO)
    # print(environment.project_config.dict())

    # cmds = global_config.commands["setup-official-tools"]
    # for cmd in cmds.run:
    #     logger.info(f"[exec command]: {cmd}")
    #     subprocess.run(cmd, env=os.environ, shell=True, cwd=os.path.expandvars(cmds.working_directory), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # print(environment.global_config.test)
    # print(environment.show())

    if args["new"]:
        generate_template(args["<name>"])
    elif args["init"]:
        generate_template(args["<name>"], in_place=True)
    elif args["gen"]:
        if args["suite"]:
            TestSuiteGenerator.generate(
                args["--name"], environment.project_config.test.case.generator["main"], case_num=args["<case-num>"]
            )
    elif args["test"]:
        if args["suite"]:
            TestRunner.run_on_suite(args["--name"], concurrency=args["<concurrency>"], exec_num=args["<case-num>"])
        elif args["case"]:
            TestRunner.run_on_case(args["<name>"])
    elif args["run"]:
        exec_command_by_name(args["<command-name>"])
    elif args["utils"]:
        if args["gen-seeds"]:
            gen_seeds(args["<n>"], args["<seed>"], args["<upper-bound>"])
    elif args["hi"]:
        print("hello!")
    elif args["server"]:
        subprocess.run(
            f"uvicorn marathon_matches_manager.__main__:app {'--reload' if args['--dev'] else ''}", shell=True
        )


if __name__ == "__main__":
    main()
