import requests

"""
Simple wrapper around requests.Session that allows to stack login sessions and 
eventually proxies or more
"""
class Session:
    def __init__(self):
        self.session = requests.Session()

    def set_auth(self, user, passw):
        self.session.auto = (user, passw)

    def get(self, url, url_params):
        self.session.get(url, params=url_params)

    def post(self, url, url_data):
        self.session.post(url, url_data)

    """
    Downloads a webpage w/o any kind of get/post data 
    """
    def wget(self, url):
        return self.session.get(url).content