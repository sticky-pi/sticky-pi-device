#!/bin/python

from subprocess import Popen
import time
import json
import requests


URL = "http://worldtimeapi.org/api/timezone/Europe/London/"


if __name__ == '__main__':
    r = requests.get(URL)

    if r.status_code != 200:
        raise Exception(f"Could not retrieve {URL}. Status: {r.status_code}")

    content = json.loads(r.content)
    unix_time = int(content['unixtime'])
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(unix_time))
    command = ["hwclock", "--set", "--date", time_str, "--utc", "--noadjfile"]
    p = Popen(command)
    exit_code = p.wait(5)
    if exit_code != 0:
        raise Exception(f"Cannot set localtime to {time_str}")

