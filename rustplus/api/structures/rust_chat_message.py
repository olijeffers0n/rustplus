class RustChatMessage:

    def __init__(self, data):
        
        self.steamId : int = data.steamId
        self.name : str = data.name
        self.message : str = data.message
        self.colour : str = data.color
        self.time : int = data.time

    def __repr__(self):
        return "RustChatMessage[steamId={}, senderName={}, message={}, colour={}, time={}]".format(self.steamId, self.name, self.message, self.colour, self.time)