import requests

"""
Simple wrapper around requests.Session that allows to stack login sessions
"""
class Session:
    def __init__(self):
        self.session = requests.Session()

    def set_auth(self, user, passw):
        self.session.auto = (user, passw)

    def wget(self, url):
        return self.session.get(url).content