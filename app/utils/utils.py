import urllib.parse


def is_url_encoded(s):
    decoded_s = urllib.parse.unquote(s)
    return s != decoded_s


async def refactor_text(text):
    words = text.split()

    if len(words) > 3:
        words = words[:3]

    refactored_text = ' '.join(words)

    return refactored_text