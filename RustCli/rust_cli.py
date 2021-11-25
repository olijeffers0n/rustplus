import threading
from flask import Flask, render_template, request
from push_receiver.push_receiver import listen, gcm_register, fcm_register
from selenium import webdriver
import time
import json
import requests
from uuid import uuid4
import json
import urllib3


class RustCli:

    def __init__(self) -> None:
        self.token = ""
        self.uuid = uuid4()


    def getConfigFile(self):
        return "rustpy.config.json"


    def readConfig(self, file):
        try:
            with open(file) as fp:
                return json.load(fp)
        except:
            return {}


    def updateConfig(self, file, data):
        with open(file, "w") as outputFile:
            json.dump(data, outputFile, indent=4, sort_keys=True)


    def getExpoPushToken(self, credentials):
        response = requests.post("https://exp.host/--/api/v2/push/getExpoPushToken", data={
            "deviceId" : self.uuid,
            "experienceId": '@facepunch/RustCompanion',
            "appId": 'com.facepunch.rust.companion',
            "deviceToken": credentials["fcm"]["token"],
            "type": 'fcm',
            "development": False
        })

        return response.json()["data"]["expoPushToken"]


    def registerWithRustPlus(self, authToken, expoPushToken):
            
        encoded_body = json.dumps({
                "AuthToken": authToken,
                "DeviceId": 'rustplus.js',
                "PushKind": 0,
                "PushToken": expoPushToken,
            }).encode('utf-8')

        http = urllib3.PoolManager()

        return http.request('POST', 'https://companion-rust.facepunch.com:443/api/push/register',
                        headers={'Content-Type': 'application/json'},
                        body=encoded_body)

    
    def clientView(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-site-isolation-trials")

        driver = webdriver.Chrome(options=options)
        driver.get("http://localhost:3000")
        
        while True:
            try:
                if str(driver.current_url).startswith("http://localhost:3000/callback"):
                    driver.close()
                    break
                time.sleep(2)
            except Exception:
                return
    

    def linkSteamWithRustPlus(self):

        thread = threading.Thread(target=self.clientView)
        thread.start()
        
        app = Flask(__name__)

        @app.route('/')
        def main():
            return render_template("pair.html")

        @app.route('/callback')
        def callback():
            self.token = request.args["token"]
            try:
                func = request.environ.get('werkzeug.server.shutdown')
                func()
            except:
                pass

            return "All Done!"

        app.run(port = 3000)

        return self.token

    def registerWithFCM(self, sender_id):
        appId = "wp:receiver.push.com#{}".format(self.uuid)
        subscription = gcm_register(appId=appId, retries=50)
        fcm = fcm_register(sender_id=sender_id, token=subscription["token"])
        res = {"gcm": subscription}
        res.update(fcm)
        return res


    def fcmRegister(self):

        print("Registering with FCM")
        fcmCredentials = self.registerWithFCM(976529667804)

        print(fcmCredentials)

        print("Fetching Expo Push Token")
        try:
            expoPushToken = self.getExpoPushToken(fcmCredentials)
        except Exception:
                print("Failed to fetch Expo Push Token")
                quit()

        # show expo push token to user
        print("Successfully fetched Expo Push Token")
        print("Expo Push Token: " + expoPushToken)

        # tell user to link steam with rust+ through Google Chrome
        print("Google Chrome is launching so you can link your Steam account with Rust+")
        rustplusAuthToken = self.linkSteamWithRustPlus()
        #rustplusAuthToken = "eyJzdGVhbUlkIjoiNzY1NjExOTg0Mzg3OTY0OTUiLCJpc3MiOjE2Mzc3NjI3MDYsImV4cCI6MTYzODk3MjMwNn0=.f7Fw8w3k1M1j11vaOUzoqQRwC4s2S1jUbwlgnjwFUCSXvwTpj6o6aqxOYk8Vuf8a4Nk7Y4aB45vlIWO9t0ogBg=="

        # show rust+ auth token to user
        print("Successfully linked Steam account with Rust+")
        print("Rust+ AuthToken: " + rustplusAuthToken)

        print("Registering with Rust Companion API")
        try:
            self.registerWithRustPlus(rustplusAuthToken, expoPushToken)
        except Exception:
            print("Failed to register with Rust Companion API")
            quit()
        print("Successfully registered with Rust Companion API.")

        # save to config
        configFile = self.getConfigFile()
        self.updateConfig(configFile, {
            "fcm_credentials": fcmCredentials,
            "expo_push_token": expoPushToken,
            "rustplus_auth_token": rustplusAuthToken,
        })

        print("FCM, Expo and Rust+ auth tokens have been saved to " + configFile)


    def on_notification(self, obj, notification, data_message):

        print(json.dumps(json.loads(notification["data"]["body"]), indent=4, sort_keys=True))


    def fcmListen(self):

        with open("rustpy.config.json", "r") as file:
            credentials = json.load(file)

        print("Listening...")

        listen(credentials=credentials["fcm_credentials"], callback=self.on_notification)

    

if __name__ == "__main__":

    cli = RustCli()

    
    cli.fcmRegister()
    cli.fcmListen()