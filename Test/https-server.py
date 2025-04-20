import http.server
import ssl
import os

PORT = 4443
SERVE_DIR = "TEST_FILES"

# Save current directory to load certs later
BASE_DIR = os.path.abspath(os.getcwd())

# Change working directory to serve TEST_FILES content
os.chdir(SERVE_DIR)

# Create the handler
handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(("0.0.0.0", PORT), handler)

# Create SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Load certs from original directory
cert_path = os.path.join(BASE_DIR, "cert.pem")
key_path = os.path.join(BASE_DIR, "key.pem")
context.load_cert_chain(certfile=cert_path, keyfile=key_path)

# Wrap socket with context
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"Serving HTTPS on https://0.0.0.0:{PORT} from directory: {os.path.abspath(SERVE_DIR)}")
httpd.serve_forever()
