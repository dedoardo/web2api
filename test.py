import web2api

api = web2api.Web2API('hosts')
r = web2api.Request()
r.hostname = 'www.gamedev.net'
r.id = 'main_search'
print api.query(r)