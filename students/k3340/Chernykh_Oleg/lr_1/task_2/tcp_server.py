import socket
import math


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ("127.0.0.1", 9999)
    server_socket.bind(server_address)

    server_socket.listen(1)
    print(f"TCP server is listening on {server_address[0]}:{server_address[1]}")

    conn, client_addr = server_socket.accept()
    print(f"Accepted connection from {client_addr}")

    try:
        data = conn.recv(1024)
        if not data:
            return

        text = data.decode("utf-8", errors="replace").strip()
        parts = text.split()
        if len(parts) != 2:
            conn.sendall("ERROR: expected two numbers 'a b'\n".encode("utf-8"))
            return

        try:
            a = float(parts[0])
            b = float(parts[1])
        except ValueError:
            conn.sendall("ERROR: invalid numbers\n".encode("utf-8"))
            return

        c = math.hypot(a, b)

        response = f"{c}\n".encode("utf-8")
        conn.sendall(response)
    finally:
        conn.close()
        server_socket.close()


if __name__ == "__main__":
    main()
