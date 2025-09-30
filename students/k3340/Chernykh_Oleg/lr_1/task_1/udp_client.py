import socket


def main() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ("127.0.0.1", 9999)

    message = "Hello, server".encode("utf-8")
    client_socket.sendto(message, server_address)

    data, server_addr = client_socket.recvfrom(4096)

    response = data.decode("utf-8", errors="replace")
    print(f"Received from server {server_addr}: {response}")

    client_socket.close()


if __name__ == "__main__":
    main()
