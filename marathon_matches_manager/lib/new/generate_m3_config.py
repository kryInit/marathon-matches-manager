import logging
from pathlib import Path

import toml

def generate_m3_config(path,data,name) -> None:
    
    dic = {}
    dic["project"] ={}
    dic["project"]["name"] = name
    
    
    dic["contest"]={}
    dic["contest"]["url"] = str(data.url)
    dic["contest"]["name"] = data.name
    dic["contest"]["sub_name"] = data.sub_name
    dic["contest"]["start_time"] = data.start_time
    dic["contest"]["time_limit"] = str(data.time_limit)
    dic["contest"]["is_rated"] = data.is_rated
    
    toml.dump(dic, open(path, mode='w'))
