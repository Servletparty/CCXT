from Auth import Keys as k

class Creds:
    def __init__(self) -> None:
        self.creds = k.get_keys()
    
    def get_creds(self):
        return self.creds