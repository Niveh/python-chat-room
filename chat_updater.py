import requests
import json
import time

CLIENT_NAME = "client.py"
UPDATER_NAME = "chat_updater.py"


def name_to_script(name):
    return name.replace(".py", "_script")


FILE_KEYS = {
    CLIENT_NAME: name_to_script(CLIENT_NAME),
    UPDATER_NAME: name_to_script(UPDATER_NAME)
}


GIST_IDS = {
    "public_ip": "ed60888796a0aaf68038ea171f481778",
    FILE_KEYS[CLIENT_NAME]: "93201d6d2a2c78ec071ae9688cc45844",
    FILE_KEYS[UPDATER_NAME]: "c72ab9071031c1d731b150094692b2a7"
}


def get_token():
    return open("api_token.txt", "r").read()


def read_client_script():
    return open(CLIENT_NAME).read()


def read_updater_script():
    return open(UPDATER_NAME).read()


def read_updater_gist():
    gist_id = GIST_IDS["chat_updater_script"]
    link = "https://api.github.com/gists/" + gist_id
    req = json.loads(requests.get(link).text)

    return req["files"][UPDATER_NAME]["content"]


def read_client_gist():
    gist_id = GIST_IDS["client_script"]
    link = "https://api.github.com/gists/" + gist_id
    req = json.loads(requests.get(link).text)

    return req["files"][CLIENT_NAME]["content"]


def is_client_updated():
    local_client = read_client_script().replace("\r", "")
    public_client = read_client_gist().replace("\r", "")

    return local_client == public_client


def is_updater_updated():
    local_updater = read_updater_script().replace("\r", "")
    public_updater = read_updater_gist().replace("\r", "")

    return local_updater == public_updater


def self_update_client():
    public_client = read_client_gist().replace("\r", "")

    with open(CLIENT_NAME, "w") as f:
        f.write(public_client)

    print(f"{CLIENT_NAME} has been updated!\nRestart your client to apply the changes.")


def self_update_updater():
    public_updater = read_updater_gist().replace("\r", "")

    with open(UPDATER_NAME, "w") as f:
        f.write(public_updater)

    print(f"{UPDATER_NAME} has been updated!\nRestart your client to apply the changes.")


def get_public_address():
    link = "http://localhost:4040/api/tunnels/command_line"
    req = requests.get(link)

    public_url = json.loads(req.text)["public_url"][6:].split(":")

    with open("latest.txt", "w+") as f:
        f.write(f"(\"{public_url[0]}\", {public_url[1]})")

    return (public_url[0], int(public_url[1]))


def get_addr_from_gist():
    gist_id = GIST_IDS["public_ip"]
    link = "https://api.github.com/gists/" + gist_id
    req = requests.get(link).text

    data = json.loads(req)["files"]["latest.txt"]["content"]
    data = data.replace("(", "").replace(")", "").replace("\"", "").split(", ")

    return (data[0], int(data[1]))


def update_latest_addr_gist():
    token = get_token()
    filename = "latest.txt"
    gist_id = GIST_IDS["public_ip"]

    content = open(filename, 'r').read()
    headers = {'Authorization': f'token {token}'}
    r = requests.patch('https://api.github.com/gists/' + gist_id,
                       data=json.dumps({'files': {filename: {"content": content}}}), headers=headers)


def update_client_gist():
    token = get_token()
    filename = CLIENT_NAME
    gist_id = GIST_IDS[FILE_KEYS[CLIENT_NAME]]

    content = open(filename, 'r').read()
    headers = {'Authorization': f'token {token}'}
    r = requests.patch('https://api.github.com/gists/' + gist_id,
                       data=json.dumps({'files': {filename: {"content": content}}}), headers=headers)


def update_updater_gist():
    token = get_token()
    filename = UPDATER_NAME
    gist_id = GIST_IDS[FILE_KEYS[UPDATER_NAME]]

    content = open(filename, 'r').read()
    headers = {'Authorization': f'token {token}'}
    r = requests.patch('https://api.github.com/gists/' + gist_id,
                       data=json.dumps({'files': {filename: {"content": content}}}), headers=headers)
