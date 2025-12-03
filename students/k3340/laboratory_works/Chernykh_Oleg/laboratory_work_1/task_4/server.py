import socket
import threading


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ("127.0.0.1", 10000)
    server_socket.bind(server_address)
    server_socket.listen(10)
    print(f"Chat server is listening on {server_address[0]}:{server_address[1]}")

    clients: list[socket.socket] = []
    clients_lock = threading.Lock()

    def broadcast(message: bytes, sender: socket.socket | None) -> None:
        with clients_lock:
            targets = list(clients)
        for sock in targets:
            if sock is sender:
                continue
            try:
                sock.sendall(message)
            except Exception:
                try:
                    sock.close()
                finally:
                    with clients_lock:
                        if sock in clients:
                            clients.remove(sock)

    def handle_client(conn: socket.socket, addr: tuple[str, int]) -> None:
        try:
            welcome = (
                f"[server] Connected to chat. Your peer: {addr[0]}:{addr[1]}\n"
                "[server] Type messages and press Enter. Empty line to quit.\n"
            ).encode("utf-8")
            conn.sendall(welcome)

            join_msg = f"[server] User {addr[0]}:{addr[1]} joined\n".encode("utf-8")
            broadcast(join_msg, sender=conn)

            while True:
                data = conn.recv(4096)
                if not data:
                    break

                text = data.decode("utf-8", errors="replace")
                if text.strip() == "":
                    break

                prefixed = f"[{addr[0]}:{addr[1]}] {text}".encode("utf-8")
                broadcast(prefixed, sender=conn)
        finally:
            with clients_lock:
                if conn in clients:
                    clients.remove(conn)
            try:
                conn.close()
            finally:
                leave_msg = f"[server] User {addr[0]}:{addr[1]} left\n".encode("utf-8")
                broadcast(leave_msg, sender=None)

    try:
        while True:
            conn, addr = server_socket.accept()
            with clients_lock:
                clients.append(conn)
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    finally:
        with clients_lock:
            for c in clients:
                try:
                    c.close()
                except Exception:
                    pass
            clients.clear()
        server_socket.close()


if __name__ == "__main__":
    main()
