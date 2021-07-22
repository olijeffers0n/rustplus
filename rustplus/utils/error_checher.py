from ..exceptions import ClientError

class ErrorChecker:
    def check(self, message) -> None:
        if message.response.error.error != "":
            raise ClientError("An Error has been returned: {}".format(str(message.response.error.error)))