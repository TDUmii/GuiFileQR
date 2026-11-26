from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import ProxyHandler, build_opener

from sharing import ShareSession


class SharingTest(TestCase):
    def test_download_only_chosen_file_then_close(self):
        client = build_opener(ProxyHandler({}))

        with TemporaryDirectory() as directory:
            file_path = Path(directory) / "Tài liệu buổi học.txt"
            payload = b"PythonMaster"
            file_path.write_bytes(payload)

            session = ShareSession(file_path, "127.0.0.1")
            try:
                with client.open(session.url, timeout=2) as response:
                    self.assertEqual(response.read(), payload)
                    disposition = response.headers["Content-Disposition"]
                    self.assertTrue(disposition.startswith("attachment;"))
                    self.assertIn(f"filename*=UTF-8''{quote(file_path.name)}", disposition)
                    self.assertEqual(response.headers["Cache-Control"], "no-store")

                address = urlsplit(session.url).netloc
                for path in ("/", "/other-file.txt"):
                    with self.assertRaises(HTTPError) as rejection:
                        client.open(f"http://{address}{path}", timeout=2)
                    self.assertEqual(rejection.exception.code, 404)
                    rejection.exception.close()

                with self.assertRaises(FileNotFoundError):
                    ShareSession(file_path.with_name("missing.txt"), "127.0.0.1")
                with self.assertRaises(FileNotFoundError):
                    ShareSession(file_path.parent, "127.0.0.1")
                with self.assertRaises(ValueError):
                    ShareSession(file_path, "0.0.0.0")
            finally:
                session.close()
                session.close()

            with self.assertRaises(URLError):
                client.open(session.url, timeout=2)


if __name__ == "__main__":
    main()
