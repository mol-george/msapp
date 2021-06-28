from flask import Flask, abort, request
from random import choice
import json
from os import environ
import requests
from time import sleep

app = Flask(__name__)

pod = environ.get('MY_POD_NAME')
nextapp = environ.get('NEXT_APP')
version = environ.get('VERSION')
delays = [0, 1, 3, 5]
codes = [200, 500, 502, 503]
counter = 1


def file_dict(file):
    '''Takes a file and returns a dictionary based on its content'''
    fd = {}
    with open(file) as f:
        for line in f:
            (key, val) = line.rstrip().replace('"', '').split("=")
            fd[key] = val
    return fd


def get_delay_code(delays, codes):
    code = choice(codes)
    delay = choice(delays)
    return delay, code

def get_headers(request):
    '''Intercepts incoming headers and returns only headers containing x-'''
    headers = {header: value for (
        header, value) in request.headers.items() if 'x-' in header.lower()}
    return headers


def get_nextmessage(tracking_headers):
    nextmessage = {}
    try:
        re = requests.get(f'http://{nextapp}/',
                          headers=tracking_headers)
        nextmessage[nextapp] = json.loads(re.text)
    except:
        nextmessage[nextapp] = "error"
    return nextmessage


def set_message(headers, nextmessage=""):
    '''Returns a dictionary containing info about the current pod and next microservice message is set'''
    message = {}
    importantheaders = {}
    global counter
    message['pod'] = pod
    if version is not None:
        message['version'] = version
    message['counter'] = counter
    if 'X-Request-Id' in headers:
        importantheaders['X-Request-Id'] = headers['X-Request-Id']
    if 'X-Dark-Header' in headers:
        importantheaders['X-Dark-Header'] = headers['X-Dark-Header']
    if importantheaders:
        message['headers'] = importantheaders
    if nextmessage:
        message[nextapp] = nextmessage[nextapp]
    counter += 1
    return message

@app.route("/")
def index():
    fd = file_dict('/etc/downward/labels')
    if 'error' in fd and fd['error'] == '1':
        delay_code = get_delay_code(delays, codes)
        delay = delay_code[0]
        code = delay_code[1]
        sleep(delay)
        return json.dumps({'pod': pod, 'delay': delay, 'code': code}), code
    else:
        headers = get_headers(request)
        if nextapp is not None:
            # Only attempt to get nextapp message if nextapp is set.
            return json.dumps(set_message(headers, get_nextmessage(headers)), sort_keys=False, indent=4)
        else:
            return json.dumps(set_message(headers), sort_keys=False, indent=4)

if __name__ == "__main__":
    # Only for debugging while developing
    app.strict_slashes = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.run(host='0.0.0.0', debug=True, port=80)
