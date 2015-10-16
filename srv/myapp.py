import bottle

@bottle.route('/')
def home():
    return '<html><head></head><body>Hello world!</body></html>'

app = bottle.default_app()
