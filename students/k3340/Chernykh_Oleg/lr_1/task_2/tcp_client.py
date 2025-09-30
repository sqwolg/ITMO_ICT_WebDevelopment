import socket


def main() -> None:
    a_str = input("Enter leg a: ").strip()
    b_str = input("Enter leg b: ").strip()

    try:
        float(a_str)
        float(b_str)
    except ValueError:
        print("ERROR: please enter valid numbers.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_address = ("127.0.0.1", 9999)
        client_socket.connect(server_address)

        message = f"{a_str} {b_str}\n".encode("utf-8")
        client_socket.sendall(message)

        data = client_socket.recv(1024)
        if not data:
            print("Server sent no data.")
            return

        response = data.decode("utf-8", errors="replace").strip()
        print(f"Result (hypotenuse): {response}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
