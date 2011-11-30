from twisted.web.resource import Resource
class Di(Resource):
    def render_GET(self, request):
        return "ok"
