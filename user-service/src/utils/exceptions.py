class InvalidCredentialsException(Exception):
    def __init__(self):
        self.message = "Incorrect username or password"
        super().__init__(self.message)


class UserBannedException(Exception):
    def __init__(self):
        self.message = "User is banned"
        super().__init__(self.message)
