#!/usr/bin/env python3
"""
Simple HTTP server to serve the FBMessage HTML interface.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Serve FBMessage Explorer')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port to serve on (default: 8080)')
    args = parser.parse_args()
    
    port = args.port
    
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Create handler
    handler = http.server.SimpleHTTPRequestHandler
    
    # Add CORS headers to allow file uploads
    class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            super().end_headers()
    
    # Start server
    with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
        print(f"FBMessage Explorer is running at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Try to open browser
        try:
            webbrowser.open(f"http://localhost:{port}")
        except:
            print("Could not open browser automatically")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

if __name__ == "__main__":
    main()
