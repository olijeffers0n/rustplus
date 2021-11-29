class Command:

    def __init__(self, sender_name, sender_steamid, time, command, args) -> None:
        
        self.sender_name = sender_name
        self.sender_steamid = sender_steamid
        self.time = time
        self.command = command
        self.args = args
