import json

import toml

from ..models.config import M3Config


def generate_testcases():
    with open("/Users/rk/Projects/marathon-matches-manager/workspace/ahc018/m3-config.toml", mode="r") as f:
        content = toml.load(f)
    print(json.dumps(content, indent=2))
    config = M3Config.parse_obj(content)
    print(config)
    print(json.dumps(json.loads(config.json()), indent=2))
