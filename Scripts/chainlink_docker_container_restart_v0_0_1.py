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
                "notification_mode":"production", #slackDebug,production
                'Target Working Parent Directory Path': '/home/{}/'.format(operating_dict['Username']),
                'Working Directory Name': '.chainlink-{}'.format(operating_dict['Network']),
                'Chainlink Node Version':'1.1.0',
                "slack_channel_webhook_url":"https://hooks.slack.com/services/..../..../....",
                "chainlink_script_directory_absolute_path":"/home/{}/".format(operating_dict["Username"]),
                "chainlink_docker_start_script_file_name":"chainlink_docker_container_start_v0_0_1.py"}

def restart_failover_chainlink_docker_container(inputDict):
    remove_docker_container_linux_command='docker rm -f {}'.format(inputDict['Container Name'])
    docker_container_remove_status=subprocess.getoutput('{}'.format(remove_docker_container_linux_command))

    linux_command="{}{}".format(inputDict["chainlink_script_directory_absolute_path"],inputDict["chainlink_docker_start_script_file_name"])

    docker_container_restart_status=subprocess.getoutput('{}'.format(linux_command))
    
    if (inputDict["notification_mode"]=="slackDebug"):
        (nakedTimeString,timeString)=get_current_dateTime()
        titleMessageDict=populate_title_and_message('Docker Container Restart Script:Failover Chainlink Docker Container Restarted {}'.format(timeString),'Failover Chainlink Docker Container Restarted Successfully')
        slack_send_channel_automated_message(titleMessageDict,'Success')
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
def slack_send_channel_automated_message(dict,titleMessageDict,state):
    if (state=='Success'):
        color="#7bf538" #green
    else:
        color="#9733EE" #red
    #alerts-link-eth-rinkeby
    url = "{}".format(dict["slack_channel_webhook_url"])
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
    return (naked_time_string,time_string)
#####################################################################################
def run_failover_function():
  restart_failover_chainlink_docker_container(input_dict)
  return
if __name__ == '__Failover__':
    run_failover_function()
