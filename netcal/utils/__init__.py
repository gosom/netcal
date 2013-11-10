import socket

def check_connection(host, port):
    """returns True if the host is readchable
    and port port is open"""
    assert isinstance(host, basestring)
    assert isinstance(port, int)
    ok = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)
    try:
        sock.connect((host, port))
    except socket.error:
        pass
    else:
        ok = True
    finally:
        sock.close()
    return ok

