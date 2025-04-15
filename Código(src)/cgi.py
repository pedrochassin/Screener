# cgi.py
from urllib.parse import parse_qs, urlparse

def parse_qs_qs(query):
    """Emula cgi.parse_qs"""
    return parse_qs(query)

def parse_header(header):
    """Emula cgi.parse_header"""
    return header, {}

def parse_multipart(*args, **kwargs):
    """Emula cgi.parse_multipart"""
    return {}

class FieldStorage:
    """Emula cgi.FieldStorage"""
    def __init__(self, *args, **kwargs):
        self.list = []
        self.file = None
    def getvalue(self, key, default=None):
        return default
    def __getitem__(self, key):
        return None