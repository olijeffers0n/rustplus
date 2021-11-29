class RustChatMessage():

    def __init__(self, data):
        
        self.steamId = data.steamId
        self.name = data.name
        self.message = str(data.message)
        self.colour = data.color
        self.time = data.time

    def __repr__(self):
        return "RustChatMessage[steamId={}, senderName={}, message={}, colour={}, time={}]".format(self.steamId, self.name, self.message, self.colour, self.time)