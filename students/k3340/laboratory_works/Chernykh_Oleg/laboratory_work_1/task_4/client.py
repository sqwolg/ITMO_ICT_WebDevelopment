import socket
import threading
import sys


def main() -> None:
    server_address = ("127.0.0.1", 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    stop_event = threading.Event()

    def receive_loop() -> None:
        try:
            while not stop_event.is_set():
                data = sock.recv(4096)
                if not data:
                    print("[client] Disconnected from server")
                    break
                sys.stdout.write(data.decode("utf-8", errors="replace"))
                sys.stdout.flush()
        finally:
            stop_event.set()

    def send_loop() -> None:
        try:
            while not stop_event.is_set():
                try:
                    line = input()
                except EOFError:
                    line = ""
                message = (line + "\n").encode("utf-8")
                try:
                    sock.sendall(message)
                except Exception:
                    break
                if line.strip() == "":
                    break
        finally:
            stop_event.set()

    t_recv = threading.Thread(target=receive_loop, daemon=True)
    t_send = threading.Thread(target=send_loop, daemon=True)
    t_recv.start()
    t_send.start()

    try:
        t_send.join()
        t_recv.join(timeout=0.2)
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        sock.close()


if __name__ == "__main__":
    main()
