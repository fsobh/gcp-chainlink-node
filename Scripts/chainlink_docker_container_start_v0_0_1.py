#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import json
import requests

operating_dict = {'Username':'username',
                    'Network':'rinkeby'}

input_dict = {'Container Name': 'link-main-node',
                'Target Working Parent Directory Path': '/home/{}/'.format(operating_dict['Username']),
                'Working Directory Name': '.chainlink-{}'.format(operating_dict['Network']),
                'Chainlink Node Version':'1.1.0'}

def start_main_chainlink_docker_container(inputDict):
    try:
        change_dir_linux_command=os.chdir('{}{}'.format(inputDict['Target Working Parent Directory Path'],inputDict['Working Directory Name']))
        linux_command="docker run --name {} -d -p 6689:6689 -v {}{}:/chainlink -it --env-file=.env smartcontract/chainlink:{} local n -p /chainlink/.password -a /chainlink/.api".format(inputDict['Container Name'],inputDict['Target Working Parent Directory Path'],inputDict['Working Directory Name'],inputDict['Chainlink Node Version'])
        #print(linux_command)
        docker_container_restart_status=subprocess.getoutput('{}'.format(linux_command))
        (nakedTimeString,timeString)=get_current_dateTime()
        if (len(docker_container_restart_status)==int(64)):
            titleMessageDict=populate_title_and_message('Docker Container Run Script:Task (1/1) {}'.format(timeString),'Chainlink Docker Container Started Successfully')
            slack_send_channel_automated_message(titleMessageDict,'Success')
        else:
            titleMessageDict=populate_title_and_message('Docker Container Run Script:Task (1/1) {}'.format(timeString),'Chainlink Docker Container Failed: {}'.format(docker_container_restart_status))
            slack_send_channel_automated_message(titleMessageDict,'Fail')
        return
    except Exception as error:
        (nakedTimeString,timeString)=get_current_dateTime()
        titleMessageDict=populate_title_and_message('Docker Container Run Script:Task (1/1) {}'.format(timeString),'Chainlink Docker Container Failed: {}'.format(error))
        slack_send_channel_automated_message(titleMessageDict,'Fail')
        return
#####################################################################################
def determine_title():
    title=(f"New Incoming Message :zap:")
    return (title)
def populate_title_and_message(title,message):
    title_and_message_dict={"title_fixed" : "{}".format(title),
                            "message_fixed" : "{}".format(message)}
    #print("{}".format(title_and_message_dict["title_fixed"]))
    return (title_and_message_dict)
def slack_send_channel_automated_message(titleMessageDict,state):
    if (state=='Success'):
        color="#7bf538" #green
    else:
        color="#9733EE" #red
    #alerts-link-eth-rinkeby
    url = "https://hooks.slack.com/services/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"
    slack_data = {
        "username": "NotificationBot",
        "icon_emoji": ":satellite:",
        #"channel" : "#somerandomcahnnel",
        "attachments": [
            {
                "color": "{}".format(color), #9733EE=red,#7bf538=green
                "fields": [
                    {
                        "title": "{}".format(titleMessageDict["title_fixed"]),
                        "value": "{}".format(titleMessageDict["message_fixed"]),
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
def get_current_dateTime():
    # mm/dd/y
    named_tuple = time.localtime() # get struct_time
    naked_time_string = time.strftime("%d%m%YT%H%M%S", named_tuple)
    time_string = time.strftime("%d/%m/%YT%H:%M:%S", named_tuple)
    #print(naked_time_string)
    #print(time_string)
    return (naked_time_string,time_string)
#####################################################################################
def run_main_function():
  start_main_chainlink_docker_container(input_dict)
  return
if __name__ == '__main__':
    run_main_function()
