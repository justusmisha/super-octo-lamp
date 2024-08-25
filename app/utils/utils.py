import urllib.parse


def is_url_encoded(s):
    decoded_s = urllib.parse.unquote(s)
    return s != decoded_s
