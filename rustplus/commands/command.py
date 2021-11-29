class Command:

    def __init__(self, sender_name, sender_steamid, message, time ) -> None:
        
        self.sender_name = sender_name
        self.sender_steamid = sender_steamid
        self.message = message
        self.time = time
