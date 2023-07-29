import http.server
import socketserver
import socket
import webbrowser
import argparse
import sys
import os
import base64
import bcrypt

# Set the port number for the server to listen on
PORT = 8000

# Choose the directory you want to serve files from
DIRECTORY_TO_SERVE = "D://"  # Current directory - "C://" or "D://Documents/"

# Function to get the local IP address of the PC
def get_local_ip():
    try:
        # Create a socket and connect to an external host (Google's public DNS server)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except socket.error:
        return "127.0.0.1"

# Function to generate a bcrypt hash from a password
def generate_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

# Function to check if a provided password matches the hashed password
def verify_password(provided_password, hashed_password):
    return bcrypt.checkpw(provided_password.encode(), hashed_password)

# Global variables to store the hashed username and password
# Replace 'your_username_here' and 'your_password_here' with your desired username and password
USERNAME = 'username'
PASSWORD_HASH = generate_password_hash('password')

class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHENTICATE(self):
        auth_header = self.headers.get('Authorization')
        if auth_header is None or 'Basic ' not in auth_header:
            self.do_AUTHHEAD()
            self.wfile.write('No authorization header received'.encode())
            return False

        # Get the provided credentials from the authorization header
        auth_decoded = base64.b64decode(auth_header.split(' ')[-1]).decode()
        provided_username, provided_password = auth_decoded.split(':')

        # Verify both username and password
        if provided_username != USERNAME or not verify_password(provided_password, PASSWORD_HASH):
            self.do_AUTHHEAD()
            self.wfile.write('Invalid credentials'.encode())
            return False

        return True

    def do_GET(self):
        if not self.do_AUTHENTICATE():
            return

        # If the authentication is successful, serve the content
        file_path = self.translate_path(self.path)
        if os.path.isdir(file_path):
            # Check if the path ends with a slash, if not, redirect to the same path with a trailing slash
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", f"{self.path}/")
                self.end_headers()
                return

            self.list_directory(file_path)
        elif os.path.isfile(file_path):
            # Check if the 'download' query parameter is present
            if self.query_exists("download"):
                self.send_head_download(file_path)
            else:
                self.send_head(file_path)

    def query_exists(self, key):
        return key in self.path and '?' in self.path

    def list_directory(self, path):
        try:
            # Open the directory and read its contents
            file_list = os.listdir(path)
            file_list.sort()

            # Generate the HTML for the directory listing
            html = "<!DOCTYPE html>\n<html><head>"
            html += "<title>File Manager</title>"
            html += "<style>"
            html += "body { font-family: Arial, sans-serif; margin: 20px; }"
            html += "h1 { text-align: center; }"
            html += "a { text-decoration: none; color: #007bff; }"
            html += "a:hover { text-decoration: underline; }"
            html += ".file-list { border-collapse: collapse; width: 100%; }"
            html += ".file-list th, .file-list td { padding: 8px; text-align: left; }"
            html += ".file-list th { background-color: #f1f1f1; }"
            html += ".file-list tr:nth-child(even) { background-color: #f2f2f2; }"
            html += ".file-list tr:hover { background-color: #ddd; }"
            html += "</style>"
            html += "</head><body>"
            html += "<h1>File Manager</h1>"
            html += "<table class='file-list'>"
            html += "<tr><th>File Name</th><th>Actions</th></tr>"
            for filename in file_list:
                file_url = self.path + filename
                download_url = f'{self.path}{filename}?download=true'
                html += f'<tr><td><a href="{file_url}">{filename}</a></td><td><a href="{download_url}" download>Download</a></td></tr>'
            html += "</table></body></html>"

            # Send the HTTP response with the directory listing
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, str(e))

    def send_head(self, path):
        # Get the file path
        path = self.translate_path(self.path)

        # Check if the file exists
        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return None

        # Send the response headers for file viewing
        try:
            file_size = os.path.getsize(path)
            f = open(path, 'rb')
            self.send_response(200)
            self.send_header("Content-type", self.guess_type(path))
            self.send_header("Content-Length", str(file_size))
            self.end_headers()

            # Send the file contents in chunks
            self.copyfile(f, self.wfile)
            f.close()
        except:
            self.send_error(500, "Server error")

    def send_head_download(self, path):
        # Get the file path
        path = self.translate_path(self.path)

        # Check if the file exists
        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return None

        # Send the response headers for file download
        try:
            file_size = os.path.getsize(path)
            with open(path, 'rb') as f:
                self.send_response(200)
                self.send_header("Content-type", "application/octet-stream")
                self.send_header("Content-Length", str(file_size))
                self.send_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
                self.end_headers()

                # Send the file contents in chunks
                self.copyfile(f, self.wfile)
        except:
            self.send_error(500, "Server error")

    def translate_path(self, path):
        return os.path.abspath(os.path.join(DIRECTORY_TO_SERVE, path.lstrip('/')))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple file server for your local network.")
    parser.add_argument("action", choices=["start", "stop"], help="Start or stop the file server.")

    args = parser.parse_args()

    if args.action == "start":
        local_ip = get_local_ip()
        Handler = CustomRequestHandler

        with socketserver.ThreadingTCPServer((local_ip, PORT), Handler) as httpd:
            print(f"Serving files at http://{local_ip}:{PORT}/")
            webbrowser.open_new_tab(f"http://{local_ip}:{PORT}/")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.shutdown()
                print("\nServer closed.")
    elif args.action == "stop":
        # To stop the server, press Ctrl+C in the terminal where the script is running.
        print("Stopping the server... (Press Ctrl+C)")
