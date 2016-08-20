import web2api


s = web2api.Session()
api = web2api.Web2API('hosts')
r = web2api.Request()
r.hostname = 'www.gamedev.net'
r.id = 'FeaturedArticles'
print api.query(r, s)