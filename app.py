from dotenv import load_dotenv
import requests
import json
import time
import os

class Jellfin:
    def __init__(self) -> None:
        self.config = {"SERVER_URL": None, "API_KEY": None}
        self.newest_log = None
        self.active_devices = None

    def get_newest_log(self):
        response = requests.get(f'{self.config["SERVER_URL"]}System/ActivityLog/Entries?api_key={self.config["API_KEY"]}&limit=1')
        json_data = json.loads(response.text)
        return json_data
    
    def idenitify_log(self, log):
        for item in log['Items']:
            if item['Type'] == 'AudioPlayback':
                self.update_current_playing()
                
    def update_current_playing(self):
        print("Fired")

    def get_active_devices(self):
        response = requests.get(f'{self.config["SERVER_URL"]}Devices/?api_key={self.config["API_KEY"]}')
        json_data = json.loads(response.text)
        active_devices = []
        for item in json_data["Items"]:
            active_devices.append(item["Name"])
        return active_devices
        

    def run(self):
        while True:
            newest_log = self.get_newest_log()
            if newest_log != self.newest_log:
                self.newest_log = newest_log
                print(newest_log)
            time.sleep(5)


app = Jellfin()
load_dotenv()
app.config["SERVER_URL"] = os.getenv("URL")
app.config["API_KEY"] = os.getenv("KEY")

if __name__ == '__main__':
    app.run()