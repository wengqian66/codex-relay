import contextlib
import importlib.machinery
import importlib.util
import io
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "codex-relay"
LOADER = importlib.machinery.SourceFileLoader("codex_relay", str(SCRIPT_PATH))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
relay = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(relay)


class UsageHandler(BaseHTTPRequestHandler):
    response_status = 200
    response_payload = {"isValid": True, "remaining": 0, "unit": "USD"}
    received_authorization = None

    def do_GET(self):
        type(self).received_authorization = self.headers.get("Authorization")
        if self.path != "/v1/usage":
            self.send_response(404)
            self.end_headers()
            return
        encoded = json.dumps(type(self).response_payload).encode("utf-8")
        self.send_response(type(self).response_status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        pass


class CodexRelayQuotaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), UsageHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = "http://127.0.0.1:%s" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def setUp(self):
        UsageHandler.response_status = 200
        UsageHandler.response_payload = {"isValid": True, "remaining": 0, "unit": "USD"}
        UsageHandler.received_authorization = None
        self.data = {
            "current": "demo",
            "relays": {"demo": {"base_url": self.base_url, "api_key": "test-key"}},
        }

    def test_fetch_usage_uses_usage_path_and_bearer_token(self):
        UsageHandler.response_payload = {"is_active": True, "remaining": 12.5, "unit": "CNY"}
        url, payload, status = relay.fetch_usage(self.base_url + "/", "test-key")

        self.assertEqual(url, self.base_url + "/v1/usage")
        self.assertEqual(status, 200)
        self.assertEqual(payload["remaining"], 12.5)
        self.assertEqual(UsageHandler.received_authorization, "Bearer test-key")

    def test_extract_usage_supports_top_level_nested_and_balance_fields(self):
        self.assertEqual(
            relay.extract_usage({"is_active": False, "remaining": 0, "unit": "USD"}),
            {"is_valid": False, "remaining": 0, "unit": "USD"},
        )
        self.assertEqual(
            relay.extract_usage({"quota": {"remaining": 8, "unit": "CNY"}}),
            {"is_valid": True, "remaining": 8, "unit": "CNY"},
        )
        self.assertEqual(
            relay.extract_usage({"isValid": True, "balance": 3.2}),
            {"is_valid": True, "remaining": 3.2, "unit": "USD"},
        )

    def test_cmd_quota_prints_normalized_result(self):
        UsageHandler.response_payload = {"isValid": True, "quota": {"remaining": 8, "unit": "CNY"}}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            relay.cmd_quota(self.data)

        self.assertEqual(
            output.getvalue(),
            "relay: demo\n"
            "usage_url: %s/v1/usage\n" % self.base_url
            + "HTTP: 200\nstatus: active\nremaining: 8 CNY\n",
        )

    def test_cmd_quota_accepts_an_explicit_relay_name(self):
        self.data["relays"]["other"] = {"base_url": self.base_url, "api_key": "other-key"}
        UsageHandler.response_payload = {"is_active": False, "balance": 1}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            relay.cmd_quota(self.data, "other")

        self.assertIn("relay: other\n", output.getvalue())
        self.assertIn("status: inactive\n", output.getvalue())
        self.assertIn("remaining: 1 USD\n", output.getvalue())


if __name__ == "__main__":
    unittest.main()
