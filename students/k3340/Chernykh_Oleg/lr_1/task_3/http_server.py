import socket
import os


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ("127.0.0.1", 8080)
    server_socket.bind(server_address)

    server_socket.listen(1)
    print(f"HTTP server is listening on http://{server_address[0]}:{server_address[1]}")

    try:
        conn, client_addr = server_socket.accept()
        print(f"Accepted connection from {client_addr}")

        try:
            request_data = conn.recv(2048)
            if not request_data:
                return

            base_dir = os.path.dirname(os.path.abspath(__file__))
            index_path = os.path.join(base_dir, "index.html")

            if os.path.exists(index_path):
                with open(index_path, "rb") as f:
                    body = f.read()

                headers = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: text/html; charset=utf-8\r\n"
                    + f"Content-Length: {len(body)}\r\n".encode("ascii")
                    + b"Connection: close\r\n"
                    + b"\r\n"
                )
                response = headers + body
            else:
                body_text = "<h1>404 Not Found</h1>"
                body = body_text.encode("utf-8")
                headers = (
                    b"HTTP/1.1 404 Not Found\r\n"
                    b"Content-Type: text/html; charset=utf-8\r\n"
                    + f"Content-Length: {len(body)}\r\n".encode("ascii")
                    + b"Connection: close\r\n"
                    + b"\r\n"
                )
                response = headers + body

            conn.sendall(response)
        finally:
            conn.close()
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
