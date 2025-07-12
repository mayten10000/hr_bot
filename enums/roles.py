from enum import Enum

class UserRole(str, Enum):
    GUEST = "guest"
    USER = 'user'
    HR ="hr"
    CANDIDATE = "candidate"
    ADMIN = "admin"
    OWNER = "owner"

    def __str__(self):
        return self.value
