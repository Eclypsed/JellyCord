from flask import Flask, request, jsonify
from dotenv import load_dotenv
from urllib.parse import urljoin
import requests
import time
import os
import math
from pypresence import Presence
from threading import Timer

class RPC:
    def __init__(self) -> None:
        self.client_id = os.getenv("CLIENT_ID")
        self.RPC_instance = Presence(self.client_id)
        self.RPC_instance.connect()

    def updateRPC(self, json_data, url, position, playstate):
        try:
            id = json_data['AlbumId']
            hover_text = json_data['Album']
        except KeyError:
            id = json_data['Id']
            hover_text = json_data['Name']

        rpc_vars = {
            "details": f"{json_data['Name']} ",
            "state": ', '.join(json_data['Artists']),
            "large_image": urljoin(url, f"Items/{id}/Images/Primary?api_key={app.api_key}"),
            "large_text": hover_text,
            "buttons": [{"label": "Streaming from Jellyfin", "url": "https://jellyfin.org/"}]
            }

        if playstate == 'True':
            rpc_vars['small_image'] = 'pause-icon'
        else:
            rpc_vars['end'] = time.time() + math.floor((json_data['RunTimeTicks'] - position)/10000000)

        self.RPC_instance.update(**rpc_vars)
        print("Updated RPC")
    
    def clearRPC(self):
        self.RPC_instance.clear()
        print("Cleared RPC")


class JellyCord:
    def __init__(self) -> None:
        self.rpc = RPC()
        self.api_key = None
        self.playstate = None
        self.queue = None
        self.last_request = None

    def send_api_request(self, data):
        notification = data['notification']
        playstate = data['playstate']

        if notification in ['PlaybackStart', 'PlaybackProgress']:
            if notification == 'PlaybackProgress' and self.playstate == playstate:
                pass
            else:
                self.playstate = playstate
                server_url = data['server']
                response = requests.get(urljoin(server_url, f"Items?ids={data['id']}&api_key={self.api_key}"))
                self.rpc.updateRPC(response.json()['Items'][0], server_url, int(data['position']), playstate)
        elif notification == 'PlaybackStop':
            self.playstate = None
            self.rpc.clearRPC()

    def check_queue(self):
        if self.last_request == 'PlaybackStop':
            self.send_api_request(self.queue)

load_dotenv()
app = JellyCord()
app.api_key = os.getenv("KEY")

api = Flask(__name__)

@api.route('/webhook', methods=['POST'])
def end_point():
    webhook_data = request.get_json()
    app.queue = webhook_data

    if webhook_data['device'] == os.getenv('DEVICE'):
        notification_type = webhook_data['notification']
        if notification_type == 'PlaybackStop':
            app.last_request = 'PlaybackStop'
            timer = Timer(2, app.check_queue)
            timer.start()
        elif notification_type in ['PlaybackStart', 'PlaybackProgress']:
            app.last_request = None
            app.send_api_request(app.queue)
    return jsonify({'message': 'Webhook recieved successfully'}), 200

if __name__ == '__main__':
    api.run(debug=True)