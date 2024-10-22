import secrets


def generate_stream_key():
    return "stream_" + secrets.token_hex(1) + secrets.token_urlsafe(32)
