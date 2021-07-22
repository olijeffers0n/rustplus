class ChatMessage():
    def __init__(self, steamID, senderName, message, colour):
        self.steamID = steamID
        self.senderName = senderName
        self.message = message
        self.colour = colour

    def __str__(self):

        return str({
            "steamID" : self.steamID,
            "senderName" : self.senderName,
            "message" : self.message,
            "colour" : self.colour
        })