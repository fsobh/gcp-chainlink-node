#!/usr/bin/python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json

def coingecko_http_get_request():
    try:
        coingecko_response = get_http_request("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
        coingecko_complete_json_response = coingecko_response.json()
        coingecko_filtered_json_response = coingecko_complete_json_response.get("ethereum").get("usd")
        return coingecko_filtered_json_response
    except Exception as coingecko_api_error:
        return coingecko_api_error

def coinpaprika_http_get_request():
    try:
        coinpaprika_response = get_http_request("https://api.coinpaprika.com/v1/tickers/eth-ethereum")
        coinpaprika_complete_json_response = coinpaprika_response.json()
        coinpaprika_filtered_json_response = coinpaprika_complete_json_response.get("quotes").get("USD").get("price")
        return coinpaprika_filtered_json_response
    except Exception as coinpaprika_api_error:
        return coinpaprika_api_error

def get_http_response_with_failover_api_provider():
    main_json_response = coingecko_http_get_request()
    if (isinstance(main_json_response, float)):
        return main_json_response
    else:
        failover_json_response = coinpaprika_http_get_request()
        if (isinstance(failover_json_response, float)):
            return failover_json_response
        else:
            return "Main & Failover API errored out"

def get_http_request(http_url, params={}, headers={}, timeout=15):
    retries=3
    backoff_factor=0.3
    retry_strategy = Retry(total=retries,read=retries,connect=retries,backoff_factor=backoff_factor,status_forcelist=(500, 502, 504))
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount('http://', adapter)
    http.mount('https://', adapter)
    try:
        return http.get(http_url,params=params,headers=headers,timeout=timeout)
    except Exception as get_http_error:
        raise get_http_error
    finally:
        http.close()

def request_success(id,data):
    result = {
        "jobRunID": id,
        "data": {
        "base asset": "ETH",
        "quote asset": "USD",
        "price": data
        },
        "statusCode": 200,
    }
    return result

def request_error(id,error):
    result = {
        "jobRunID": id,
        "error": "{}".format(error),
        "statusCode": 500,
    }
    return result

def clean_float_response(float_number):
    return "{:.2f}".format(float_number)

def adapter(input_request):
    job_run_id = input_request.get('id','1')
    requested_json_response = get_http_response_with_failover_api_provider()
    if (isinstance(requested_json_response, float)):
        requested_json_response=clean_float_response(requested_json_response)
        return request_success(job_run_id,requested_json_response)
    else:
        return request_error(job_run_id,requested_json_response)

def gcp_cfn_handler(request):
    submit_json_response=adapter(request.json)
    return json.dumps(submit_json_response)
