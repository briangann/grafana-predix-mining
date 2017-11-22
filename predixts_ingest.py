#!/usr/bin/env python
"""
Sends data to Predix
"""
# https://github.com/liris/websocket-client
# pip install websocket-client --upgrade
from pprint import pprint
import json
import time
import base64
import ssl
import os
import requests
import websocket

def get_auth_token():
    client_id = 'grafana'
    client_secret = 'iseegraphs'
    b64Val = base64.b64encode('{}:{}'.format(client_id, client_secret))
    headers = {'Authorization': 'Basic {}'.format(b64Val)}
    url = 'https://1b0a5256-af02-4ca6-92eb-3574d0175721.predix-uaa.run.aws-usw02-pr.ice.predix.io/oauth/token'  # noqa
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'response_type': 'token',
        'grant_type': 'client_credentials'}
    # print headers
    # print url
    # print payload
    response = requests.post(url, data=payload, headers=headers)
    response = response.json()
    print response
    access_token = response['access_token']
    expires_in = response['expires_in']
    return {
        'token': access_token,
        'expires_in': expires_in}

def send_to_predixts(token, data):
    ingestURL = 'wss://gateway-predix-data-services.run.aws-usw02-pr.ice.predix.io/v1/stream/messages'  # noqa
    queryURL = 'https://time-series-store-predix.run.aws-usw02-pr.ice.predix.io/v1/datapoints'  # noqa
    ingestZone = 'b4991946-0d50-4d34-ba1a-9e7ff8417c28'
    queryZone = 'b4991946-0d50-4d34-ba1a-9e7ff8417c28'

    extraHeaders = []
    extraHeaders.append('Authorization: Bearer {}'.format(token))
    extraHeaders.append('Predix-Zone-id: {}'.format(ingestZone))

    #print 'IngestURL {}'.format(ingestURL)
    #print extraHeaders
    # proxy = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))  # noqa
    # http_proxy_host=host and http_proxy_port=80
    # ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws = websocket.WebSocket()
    ws.connect(ingestURL, header=extraHeaders)
    ws.send(json.dumps(data))
    result = ws.recv()
    #print "Received '%s'" % result
    ws.close()
    return result
