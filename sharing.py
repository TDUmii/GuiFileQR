from ipaddress import IPv4Address
from pathlib import Path
from secrets import token_urlsafe
from threading import Thread

from flask import Flask, abort, send_file
from werkzeug.serving import WSGIRequestHandler, make_server


class QuietRequestHandler(WSGIRequestHandler):
    def log_request(self, code="-", size="-"):
        # Keep the temporary download link out of request logs.
        pass


class ShareSession:
    def __init__(self, file_path: Path, host: str):
        self.file_path = Path(file_path).absolute()
        if not self.file_path.is_file():
            raise FileNotFoundError("Select an existing regular file.")
        with self.file_path.open("rb"):
            pass

        address = IPv4Address(host)
        if address.is_unspecified or address.is_multicast or int(address) == 0xFFFFFFFF:
            raise ValueError("Select a specific local IPv4 address.")
        app = Flask(__name__, static_folder=None)
        download_path = f"/{token_urlsafe(24)}"

        @app.get(download_path)
        def download():
            if self._server is None:
                abort(404)
            try:
                return send_file(self.file_path, as_attachment=True)
            except OSError:
                abort(404)

        @app.after_request
        def prevent_caching(response):
            response.headers["Cache-Control"] = "no-store"
            return response

        try:
            self._server = make_server(
                str(address), 0, app, threaded=True, request_handler=QuietRequestHandler
            )
        except SystemExit as error:
            # Werkzeug exits on a bind failure. Report it to the desktop caller.
            raise OSError(f"Could not bind the sharing server to {address}.") from error

        self.url = f"http://{address}:{self._server.port}{download_path}"
        try:
            Thread(
                target=self._server.serve_forever,
                kwargs={"poll_interval": 0.05},
                daemon=True,
            ).start()
        except Exception:
            self._server.server_close()
            raise

    def close(self):
        server = self._server
        if server is None:
            return

        self._server = None
        server.shutdown()
        server.server_close()
