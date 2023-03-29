import socket

class HttpMessage:
    def __init__(self, response, start_line='HTTP/1.1 200 OK') -> None:
        self.response = response
        self.start_line = start_line
        self.http_dict = {'start_line': self.start_line}
        self.new_response_msg = response

    def parse_http(self) -> None:
        head, body = self.response.split('\r\n\r\n')
        headers = head.split('\r\n')
        self.start_line = headers[0]
        self.http_dict = {'start_line': self.start_line}

        for header in headers[1:]:
            key, value = header.split(':')
            self.http_dict[key] = value
        
        if (body != ''):
            self.http_dict['body'] = body
    
    def to_http(self) -> None:
        
        self.new_response_msg = self.http_dict['start_line']