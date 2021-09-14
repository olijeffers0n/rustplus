class ChatMessage():

    def __init__(self, steamID, senderName, message, colour):
        
        self.steamID = steamID
        self.senderName = senderName
        self.message = message
        self.colour = colour

    def __repr__(self):

        return "Chat Message (steamID = {} | senderName = {} | message = {} | colour = {})".format(self.steamID, self.senderName, self.message, self.colour)