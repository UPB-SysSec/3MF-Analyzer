"""Defines a simple server that serves static files from a given directory and logs the requests."""
import json
import logging
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

from .. import SERVER_NAME, SERVER_PORT, STATIC_FILE_DIR_DST


class LoggingServer(SimpleHTTPRequestHandler):
    """Simple server that serves static files from a given directory and logs the get requests.
    The filepath of the logfile can be changed through post requests."""

    data = {"logfile": None}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=STATIC_FILE_DIR_DST, **kwargs)

    def _set_response(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _write_log(self, info):
        if self.data["logfile"] is not None:
            with open(self.data["logfile"], "a", encoding="utf-8") as logfile:
                logfile.write(f"{datetime.now().isoformat()} | {info}\n")
                logging.info("Logged '%s' to %s", info, self.data["logfile"])
        else:
            logging.info(info)

    def do_GET(self):
        """Writes the requests to the specified logfile and
        then delegates the request to the superclass to server static files."""

        self._write_log(self.path)
        super().do_GET()

    def do_POST(self):
        """Expects the request to have JSON encoded data with {"logfile": <path>}.
        Will set the logfile location to the given path."""

        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(post_data)
        if "logfile" in data:
            self.data["logfile"] = data["logfile"]

        self._set_response()
        self.wfile.write(f'Successfully set logfile to {data["logfile"]}'.encode("utf-8"))


def start_server():
    """Starts the logging webserver and runs it until the process is terminated."""

    with HTTPServer((SERVER_NAME, SERVER_PORT), LoggingServer) as httpd:
        logging.info("Running HTTP server at %s", SERVER_PORT)
        httpd.serve_forever()
