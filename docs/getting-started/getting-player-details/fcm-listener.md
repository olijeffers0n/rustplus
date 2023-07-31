# FCM Listener

Should you need to listen for additional messages, like pairing requests, this is built into the library too!

{% code title="main.py" %}
```python
from rustplus import FCMListener
import json

with open("rustplus.py.config.json", "r") as input_file:
    fcm_details = json.load(input_file)

class FCM(FCMListener):
    
    def on_notification(self, obj, notification, data_message):
        print(notification)
        
FCM(fcm_details).start()
```
{% endcode %}

The `on_notification` method will be called everytime a message is recieved from the game server.

The `rustplus.py.config.json` is the file created by the RustCli, when you register for FCM notifications. See:

{% content-ref url="./" %}
[.](./)
{% endcontent-ref %}



