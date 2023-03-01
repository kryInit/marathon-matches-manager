import json

from ..environment import environment


def generate_testcases():
    print(environment)
    print(environment.project_config)
    print(json.dumps(json.loads(environment.project_config.json()), indent=2))
