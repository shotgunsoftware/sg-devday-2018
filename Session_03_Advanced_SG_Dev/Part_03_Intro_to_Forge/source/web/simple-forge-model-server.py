
# TODO: generate server.pem in the parent directory with the following command:
#    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# run as follows:
#    python simple-forge-model-server.py
# then in your browser, visit this url to ensure it is working:
#    https://localhost:4443

# Based on this gist: https://gist.github.com/dergachev/7028596

import BaseHTTPServer, SimpleHTTPServer
import requests
import ssl

FORGE_AUTH_URL = "https://developer.api.autodesk.com/authentication/v1/authenticate"


class ForgeModelRequestServer(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/token":
            # NOTE: there is a lack of proper authentication here. You'll need
            # to consider where and how you might run code like this. You should
            # never expose access tokens on a non secure connection or on a
            # non-private network. This is purely for demo purposes and should
            # not be considered ready for production
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self._get_forge_token())
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def _get_forge_token(self):

        # TODO: You will first need to register your app with Forge. Once you've
        # done that, you can test your code by including the id/secret here. For
        # production though, you'll want to externalize these values.
        client_id = 1234      # TODO
        client_secret = 1234  # TODO

        result = requests.post(
            FORGE_AUTH_URL,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
                "scope": "viewables:read"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        result.raise_for_status()
        return result.json()["access_token"]


httpd = BaseHTTPServer.HTTPServer(('localhost', 4443), ForgeModelRequestServer)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile='../server.pem', server_side=True)
httpd.serve_forever()
