import socket

def tcp_port_check(ip: str, port: int, timeout: float = 2.0):
    """Try to connect to a TCP port. Returns (success, message)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.close()
        return True, f"tcp {port} open"
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return False, f"tcp {port} error: {e}"
