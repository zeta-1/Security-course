"""
*** Author:         Laurent Hayez
*** Date:           24 november 2015
*** Description:    Implementation of a simple HTTP proxy server.
***                 It checks in a black list whether a url can be requested or not
"""
import re

from requests import get
from http.server import BaseHTTPRequestHandler, HTTPServer


class HTTPProxy(BaseHTTPRequestHandler):

    @classmethod
    def parse_blacklist(cls):
        bl_file = open('blacklist.txt', 'r')
        # for all the lines in the blacklist.txt file, the following is applied:
        # ads.* => ads\.\* via re.escape
        # ads\.\* => ads\..* via .replace('\*', '.*') (Same for all lines in the file)
        # Every such element => elem1|elem2|elem3|... via '|'.join()
        # This string is compiled to a regex object which can be used to match the url.
        # Note: had to replace \| because it somehow escaped it too...
        cls.blacklist = re.compile(('|'.join([re.escape(x).replace('\\*', '.*').replace('\n', '')
                                              for x in bl_file])).replace('\|', '|'))



    def do_GET(self):
        if self.treat_request(self.headers['host']):
            request = get(self.path)
            self.send_response(request.status_code)
            self.send_header('Content-type', request.headers.get('content-type'))
            self.end_headers()
            self.wfile.write(request.content)
        else:
            self.send_response(403)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write('<html><head><title>Error 403: Forbidden Access. </title></head>'.encode('utf-8'))
            self.wfile.write('<body><h1>Error 403: Forbidden Access.</h1>'.encode('utf-8'))
            self.wfile.write('<p>Content blocked by proxy</p></body></html>'.encode('utf-8'))

    def treat_request(self, url):
        return False if self.blacklist.match(url) else True


def main():
    HTTPProxy.parse_blacklist()
    server = HTTPServer(('', 9999), HTTPProxy)
    print("HTTP proxy running.")
    server.serve_forever()

if __name__ == '__main__':
    main()
