import socket


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ("127.0.0.1", 9999)
    server_socket.bind(server_address)

    print(f"UDP server is listening on {server_address[0]}:{server_address[1]}")

    data, client_addr = server_socket.recvfrom(4096)

    message = data.decode("utf-8", errors="replace")
    print(f"Received from client {client_addr}: {message}")

    response = "Hello, client".encode("utf-8")
    server_socket.sendto(response, client_addr)

    server_socket.close()


if __name__ == "__main__":
    main()
