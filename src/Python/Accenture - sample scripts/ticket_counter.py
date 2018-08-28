#!/bin/python

import requests
import re
import datetime
import sys
import getpass


password = getpass.getpass('Enter your accenture password: ')

def script_usage():
    print("Wrong number of arguments, run script with with 1 or 2 arguments.")
    print("Example for Ireland => 'python script.py 28676 i'")
    print("Example for Frankfurt => 'python script.py  22705")


now = datetime.datetime.now()

if len(str(now.month)) == 1:
    month = "0" + str(now.month)


time_entries = "-".join([str(x) for x in [now.year, month, now.day]])
URL_PATTERN = "https://mywizardameuapi.accenture.com/v1/Tickets/GetModifiedTicketsByAsc/{project_id}/?LastModifiedStartDateTime={start_time}T13:55:57.753&LastModifiedEndDateTime={end_time}T10:51:31.987&BatchSize=3000"


#Frankfurt action, change URL
if len(sys.argv) == 2:
    URL_PATTERN = URL_PATTERN.replace("eu", "")


#Provided 0 or more than 2 arguments, remember the script is the first argument.
elif len(sys.argv) == 1 or len(sys.argv) > 3:
    script_usage()
    exit()

result = requests.get(URL_PATTERN.format(project_id=sys.argv[1], start_time="2012-01-01", end_time=time_entries),auth=('victor.georgiev@accenture.com', password))

if result.status_code != 200:
    print("Sorry, there is something wrong with your url or authentication.")
    exit()


number_of_tickets = re.findall(r'\d+', result.text)[0]


print("Total numbef of tickets: " +  str(number_of_tickets))
