#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import json
import requests

operating_dict = {'Username':'username',
                    'Main Network':'eth', #eth, poly, arb, bsc
                    'Network':'mainnet'} #mumbai, rinkeby, mainnet

slack_webhook_dict={"alerts-link-eth-mainnet":"https://hooks.slack.com/services/..../..../...."}

input_dict = {'Main Container Name': 'link-main-node',
                'Failover Container Name': 'link-failover-node',
                'Main Container Port': '6689',
                'Failover Container Port': '6687',
                "notification_mode":"production", #slackDebug,production
                'Target Working Parent Directory Path': '/home/{}/'.format(operating_dict['Username']),
                'Working Directory Name': '.chainlink-{}'.format(operating_dict['Network']),
                'Main Container .env': '.env',
                'Failover Container .env': '.env',
                'Keystore Password Directory Path': '.password',
                'API Directory Path': '.api',
                'Chainlink Node Version':'1.1.0',
                "slack_channel_webhook_url":"{}".format(slack_webhook_dict['alerts-link-{}-{}'.format(operating_dict['Main Network'], operating_dict['Network'])])}


def start_chainlink_docker_container(script_input_2,inputDict):
    try:
        change_dir_linux_command=os.chdir('{}{}'.format(inputDict['Target Working Parent Directory Path'],inputDict['Working Directory Name']))

        docker_container_name = inputDict['{} Container Name'.format(script_input_2)]
        docker_container_port = inputDict['{} Container Port'.format(script_input_2)]
        docker_container_env = inputDict['{} Container .env'.format(script_input_2)]

        linux_command="docker run --name {} -d -p {}:6689 -v {}{}:/chainlink -it --env-file={} smartcontract/chainlink:{} local n -p /chainlink/{} -a /chainlink/{}".format(docker_container_name,docker_container_port,inputDict['Target Working Parent Directory Path'],inputDict['Working Directory Name'],docker_container_env,inputDict['Chainlink Node Version'],inputDict['Keystore Password Directory Path'],inputDict['API Directory Path'])

        docker_container_restart_status=subprocess.getoutput('{}'.format(linux_command))
        (nakedTimeString,timeString)=get_current_dateTime()
        if (len(docker_container_restart_status)==int(64)):
            titleMessageDict=populate_title_and_message('Docker Container Run Script:Task (1/1) {}'.format(timeString),'Chainlink Docker Container Started Successfully')
            slack_send_channel_automated_message(inputDict,titleMessageDict,'Success')
        else:
            titleMessageDict=populate_title_and_message('Docker Container Run Script:Task (1/1) {}'.format(timeString),'Chainlink Docker Container Failed: {}'.format(docker_container_restart_status))
            slack_send_channel_automated_message(inputDict,titleMessageDict,'Fail')
        return

    except Exception as error:
        (nakedTimeString,timeString)=get_current_dateTime()
        titleMessageDict=populate_title_and_message('Docker Container Run Script: Start Task (1/1) {}'.format(timeString),'Chainlink Docker Container Failed: {}'.format(error))
        slack_send_channel_automated_message(inputDict,titleMessageDict,'Fail')
        return

def restart_chainlink_docker_container(script_input_2,inputDict):
    try:
        remove_docker_container_linux_command='docker rm -f {}'.format(inputDict['{} Container Name'.format(script_input_2)])
        docker_container_remove_status=subprocess.getoutput('{}'.format(remove_docker_container_linux_command))

        start_chainlink_docker_container(script_input_2,inputDict)

        return
    except Exception as error:
        (nakedTimeString,timeString)=get_current_dateTime()
        titleMessageDict=populate_title_and_message('Docker Container Run Script: Restart Task (1/1) {}'.format(timeString),'Chainlink Docker Container Failed: {}'.format(error))
        slack_send_channel_automated_message(inputDict,titleMessageDict,'Fail')
        return


##########################################################################################################################################################################
def determine_title():
    title=(f"New Incoming Message :zap:")
    return (title)

def populate_title_and_message(title,message):
    title_and_message_dict={"title_fixed" : "{}".format(title),
                            "message_fixed" : "{}".format(message)}
    return (title_and_message_dict)

def slack_send_channel_automated_message(dict,titleMessageDict,state):
    if (state=='Success'):
        color="#7bf538" #green
    else:
        color="#9733EE" #red

    url = "{}".format(dict["slack_channel_webhook_url"])
    slack_data = {
        "username": "NotificationBot",
        "icon_emoji": ":satellite:",
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
    # dd/mm/y
    named_tuple = time.localtime() # get struct_time
    naked_time_string = time.strftime("%d%m%YT%H%M%S", named_tuple)
    time_string = time.strftime("%d/%m/%YT%H:%M:%S", named_tuple)
    return (naked_time_string,time_string)
##########################################################################################################################################################################
def run_main_function():
    script_fn_arg1 = sys.argv[1] #Options= Start, Restart
    script_container_name_arg2 = sys.argv[2] #Options= Main, Failover

    if (script_fn_arg1 == 'Start'):
        start_chainlink_docker_container(script_container_name_arg2,input_dict)
    else:
        restart_chainlink_docker_container(script_container_name_arg2,input_dict)
    return

if __name__ == '__main__':
    run_main_function()
