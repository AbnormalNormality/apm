from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep
from typing import Any
from json import dumps, loads
from datetime import datetime
from apm import FunctionRegistry


class APMServer:
    def __init__(self) -> None:
        self.port: int = 0
        self.ip: str = ""
        self.running: bool = False

        self.socket: socket | None = None

        self.event = FunctionRegistry()

    def start(self, port: int, backlog: int = 1):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        self.socket.bind(("0.0.0.0", port))
        self.socket.listen(backlog)

        self.port = port
        self.running = True

        running_thread = Thread(target=self.keep_alive)
        running_thread.start()

        accept_thread = Thread(target=self.accept_clients, daemon=True)
        accept_thread.start()

    def get_ip(self) -> str:
        return gethostbyname(gethostname())

    def keep_alive(self):
        while self.running:
            sleep(1)

    def stop(self):
        if self.socket:
            self.running = False
            self.socket.close()

    def accept_clients(self):
        while self.running:
            if self.socket:
                client_socket, _ = self.socket.accept()
                Thread(target=self.handle_client,
                       args=(client_socket, )).start()

    def handle_client(self, client_socket: socket):
        with client_socket:
            while self.running:
                raw_data = client_socket.recv(1024)

                if not raw_data:
                    break

                data = decode_message(raw_data)

                on_message = self.event.on_message
                if on_message:
                    on_message(client_socket, data)

    def __enter__(self) -> "APMServer":
        return self

    def __exit__(self, *_):
        self.stop()


def decode_message(raw_data: bytes) -> dict:
    data = loads(raw_data.decode("utf-8"))

    data["encodeTime"] = datetime.fromisoformat(data["encodeTime"])
    data["decodeTime"] = datetime.now()

    return data


def encode_message(message: Any) -> bytes:
    data = {
        "data": message,
        "encodeTime": datetime.now().isoformat()
    }
    return dumps(data).encode("utf-8")


__all__ = ["APMServer", "decode_message", "encode_message"]

if __name__ == '__main__':
    server = APMServer()

    @server.event
    def on_message(client_socket: socket, data: dict):
        print(data)

    server.start(2542)
