from Auth import Keys as k

class Creds:
    def __init__(self,futures=True) -> None:
        if futures:
            self.creds = k.get_keys_futures()
        else:
            self.creds = k.get_keys()
    
    def get_creds(self):
        return self.creds