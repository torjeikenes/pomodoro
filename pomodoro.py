#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Distributed under terms of the MIT license.

"""
Program for handling pomodoro timers
"""

import json
import argparse
from datetime import datetime, timedelta
import copy
import os
import subprocess
from pathlib import Path

home = str(Path.home())

file = home+"/bin/data.json"
datetimeFormat = '%Y-%m-%dT%H:%M:%S.%f'
pomodoroLen = 25
breakLen = 5

x = {
    "start": 0,
    "end" : 0,
    "length" : pomodoroLen,
    "type" : "none"
    }

def main():
    if args.file:
        file = args.file

    if args.pomodoro:
        newPomodoro(int(args.pomodoro))


    if args.sbreak:
        newBreak(int(args.sbreak))

    if args.next:
        nextTimer()

    if args.check:
        checkTime()

def nextTimer():
    try:
        with open(file, 'r') as f:
            try:
                lines = f.read().splitlines()
                line = lines[-1]
                data = json.loads(line)
            except Exception as e:
                raise Exception("Not valid json format")
    except Exception as e:
        return

    if (data["type"] == "pomodoro") and (data["end"] != 0):
        newBreak(breakLen)
    elif (data["type"] == "break") and (data["end"] != 0):
        newPomodoro(pomodoroLen)

def newBreak(length):
    data = copy.copy(x)
    now = datetime.now().strftime(datetimeFormat)

    data["start"] = now
    data["type"] = "break"
    data["length"] = length
    writeToFile(data)

def newPomodoro(length):
    data = copy.copy(x)
    now = datetime.now().strftime(datetimeFormat)

    data["start"] = now
    data["type"] = "pomodoro"
    data["length"] = length
    data["end"] = 0
    writeToFile(data)

def writeToFile(data):
    mode = 'a' if os.path.exists(file) else 'w'

    with open(file, mode) as f:
        f.write(json.dumps(data))
        f.write("\n")

def checkTime():
    try:
        with open(file, 'r') as f:
            try:
                lines = f.read().splitlines()
                line = lines[-1]
                data = json.loads(line)
            except Exception as e:
                raise Exception("Not valid json format")
    except Exception as e:
        print("N/A")
        return

    cntd = "00:00"

    sumToday = 0
    today = datetime.today().date()
    for l in lines:
        lineData = json.loads(l)
        start = datetime.strptime(lineData["start"], datetimeFormat)
        if (lineData["end"] != 0) and (start.date() == today) and (lineData['type'] == 'pomodoro'):
            sumToday += 1

    if data["end"] == 0:
        time = datetime.strptime(data["start"], datetimeFormat)
        endtime = time + timedelta(minutes=int(data["length"]))
        now = datetime.now()
        diff = endtime - now
        if endtime < now:
            notify(data)
            data["end"] = endtime.strftime(datetimeFormat)
            lines[-1] = json.dumps(data)
            cntd = "00:00"
            with open(file, 'w') as f:
                f.write('\n'.join(lines) + '\n')
        else:
            cntd = ':'.join(str(diff).split(':')[1:])
            cntd = cntd.split('.')[0]

    tp = data["type"][0].upper()
    returnString = "{} {} {}".format(sumToday, tp, cntd)
    print(returnString)

def notify(data):
    tp = data['type']
    if (tp == 'pomodoro'):
        message = "Time is up!\nTake a break."
    elif (tp == 'break'):
        message = "Break is over!\nGet back to work."
    else:
        message = "Time is up"

    subprocess.Popen(['notify-send', message])
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--file", "-f", help="Set json file")
    parser.add_argument("--pomodoro", "-p", const=pomodoroLen, nargs='?', help="Start a pomodoro timer")
    parser.add_argument("--sbreak", "-b", const=breakLen, nargs='?',help="Start a break timer")
    parser.add_argument("--check", "-c", action='store_true',help="Check time")
    parser.add_argument("--next", "-n", action='store_true',help="Start next timer")

    args = parser.parse_args()
    main()
