import socket


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ("127.0.0.1", 8081)
    server_socket.bind(server_address)

    server_socket.listen(5)
    print(f"Journal HTTP server is listening on http://{server_address[0]}:{server_address[1]}")

    journal: dict[str, list[str]] = {}

    try:
        while True:
            conn, client_addr = server_socket.accept()
            try:
                request_data = conn.recv(4096)
                if not request_data:
                    continue

                try:
                    head, body = request_data.split(b"\r\n\r\n", 1)
                except ValueError:
                    head, body = request_data, b""

                lines = head.split(b"\r\n")
                if not lines:
                    continue
                request_line = lines[0].decode("latin1", errors="replace")
                method, path, _ = (request_line.split(" ", 2) + [""] * 3)[:3]

                headers: dict[str, str] = {}
                for raw in lines[1:]:
                    if b":" in raw:
                        name, value = raw.split(b":", 1)
                        headers[name.decode("latin1").strip().lower()] = value.decode("latin1").strip()

                content_length = int(headers.get("content-length", "0") or "0")
                body_bytes = body
                to_read = max(0, content_length - len(body_bytes))
                while to_read > 0:
                    chunk = conn.recv(min(4096, to_read))
                    if not chunk:
                        break
                    body_bytes += chunk
                    to_read -= len(chunk)

                if method.upper() == "POST" and path == "/add":
                    form = parse_urlencoded(body_bytes.decode("utf-8", errors="replace"))
                    discipline = (form.get("discipline") or "").strip()
                    grade = (form.get("grade") or "").strip()

                    if discipline and grade:
                        journal.setdefault(discipline, []).append(grade)

                    send_redirect(conn, "/")
                    continue

                html = render_index_html(journal)
                send_html(conn, html)
            finally:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                conn.close()
    finally:
        server_socket.close()


def parse_urlencoded(data: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for pair in data.split("&") if data else []:
        if "=" in pair:
            k, v = pair.split("=", 1)
        else:
            k, v = pair, ""
        key = url_decode(k)
        val = url_decode(v)
        result[key] = val
    return result


def url_decode(s: str) -> str:
    s = s.replace("+", " ")
    out_bytes = bytearray()
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "%" and i + 2 < len(s):
            hex_part = s[i + 1 : i + 3]
            try:
                out_bytes.append(int(hex_part, 16))
                i += 3
                continue
            except ValueError:
                pass
        out_bytes.extend(ch.encode("utf-8", errors="replace"))
        i += 1
    return out_bytes.decode("utf-8", errors="replace")


def render_index_html(journal: dict[str, list[str]]) -> str:
    rows: list[str] = []
    for discipline in sorted(journal.keys(), key=lambda x: x.lower()):
        grades = ", ".join(journal.get(discipline, [])) or "—"
        rows.append(f"<tr><td>{escape_html(discipline)}</td><td>{escape_html(grades)}</td></tr>")

    table_html = (
        "<table border=1 cellpadding=6 cellspacing=0>"
        "<thead><tr><th>Дисциплина</th><th>Оценки</th></tr></thead>"
        f"<tbody>{''.join(rows) if rows else '<tr><td colspan=2>Пока пусто</td></tr>'}</tbody>"
        "</table>"
    )

    form_html = (
        "<form method=POST action=/add>"
        "<label>Дисциплина: <input name=discipline required></label> "
        "<label>Оценка: <input name=grade required></label> "
        "<button type=submit>Добавить</button>"
        "</form>"
    )

    return (
        "<!doctype html>"
        "<html lang=ru><head><meta charset=utf-8>"
        "<title>Журнал</title>"
        "<meta name=viewport content='width=device-width, initial-scale=1'>"
        "<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:720px;margin:24px auto;padding:0 12px}h1{font-size:22px;margin:0 0 16px}form{margin:16px 0}input{margin-right:8px}</style>"
        "</head><body>"
        "<h1>Журнал оценок</h1>"
        f"{table_html}"
        f"{form_html}"
        "</body></html>"
    )


def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def send_html(conn: socket.socket, html: str) -> None:
    body = html.encode("utf-8")
    headers = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        + f"Content-Length: {len(body)}\r\n".encode("ascii")
        + b"Connection: close\r\n"
        + b"\r\n"
    )
    conn.sendall(headers + body)


def send_redirect(conn: socket.socket, location: str) -> None:
    body = f"<a href=\"{location}\">See Other</a>".encode("utf-8")
    headers = (
        b"HTTP/1.1 303 See Other\r\n"
        + f"Location: {location}\r\n".encode("latin1")
        + f"Content-Length: {len(body)}\r\n".encode("ascii")
        + b"Content-Type: text/html; charset=utf-8\r\n"
        + b"Connection: close\r\n"
        + b"\r\n"
    )
    conn.sendall(headers + body)


if __name__ == "__main__":
    main()
