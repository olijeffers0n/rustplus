---
description: This will show you how to get your personal player details using the RustCli
---

# Getting Player Details

This process is designed to be as easy as possible for you to get your details.\
\
The Steam ID is unique to your steam account, so can be used for any server you connect to. However, the `PlayerToken` is unique to each server & player. There are two ways to get this data:

#### As a Server Owner:

You can go to the server files where you will find a database called `player.tokens.db` containing all of these codes. You can use a tool such as [this](https://sqlitebrowser.org/) to get the codes, or access them programmatically.

#### **As a player:**

There is a [Chrome Extension](https://chrome.google.com/webstore/detail/rustpluspy-link-companion/gojhnmnggbnflhdcpcemeahejhcimnlf?hl=en) so that you can automatically sign in with the Facepunch servers and get your details. Once installed, click on its icon to be redirected to the login page. Follow the sign in instructions and you will land on my website with a box of FCM Details you can either,&#x20;

1\) Copy to Clipboard \
2\) Download to file \
3\) Use on the website to - get this - listen for notifications on the web!

### Web Listener:

This will allow you to listen for paring notifications without even opening an IDE. The messages are listened for, and then sent to your browser via a WebSocket connection. If you have any issues with them not coming through you can refresh the page and they should be there!

Obviously, you can still listen from Python and see the docs here:

{% content-ref url="fcm-listener.md" %}
[fcm-listener.md](fcm-listener.md)
{% endcontent-ref %}

When you refresh the page it will store whatever you had in that box for next time as each time you generate new details it invalidates your previous ones. To listen for notifications click "Listen for notifications" in the middle.

{% hint style="info" %}
Note: If you have previously already paired with the server you will need to unpair and re-pair.
{% endhint %}

In order to get your data, you need to:

* Click the Chrome extension icon to open the Facepunch Page
* Login through Steam to authenticate yourself
* You will be redirected to my page where you will have a box of credentials at the top. THESE ARE NOT YOUR LOGIN CREDENTIALS.
* The box at the bottom contains all FCM Notifications.&#x20;
* In-Game, send a pairing notification, You should get data like this:

```
{
    "desc": "",se
    "id": "",
    "img": "",
    "ip": "", <- This is the IP 
    "logo": "",
    "name": "",
    "playerId": "", <- This is your steam player ID
    "playerToken": "", <- This is your unique token
    "port": "", <- This is the token
    "type": "",
    "url": ""
}
```

You can then use these details in the Python Wrapper here:

```python
rust_socket = RustSocket("IPADDRESS",  "PORT", 64BITSTEAMID, PLAYERTOKEN)
```

