import os
import sys
import urllib.parse

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import app


# WSGI middleware to accurately resolve Vercel serverless request path
class VercelPathFixer:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query = environ.get("QUERY_STRING", "")
        params = urllib.parse.parse_qs(query)
        if "__path__" in params and params["__path__"]:
            real_path = params["__path__"][0]
            if not real_path.startswith("/"):
                real_path = "/" + real_path
            environ["PATH_INFO"] = real_path
            del params["__path__"]
            environ["QUERY_STRING"] = urllib.parse.urlencode(params, doseq=True)
        else:
            path = environ.get("PATH_INFO", "")
            for prefix in ["/api/index.py", "/api/index"]:
                if path == prefix:
                    environ["PATH_INFO"] = "/"
                    break
                elif path.startswith(prefix + "/"):
                    environ["PATH_INFO"] = path[len(prefix):]
                    break
        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathFixer(app.wsgi_app)

# Vercel entrypoints
handler = app
application = app
