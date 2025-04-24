from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep
from typing import Any, Callable
from json import dumps, loads
from datetime import datetime
from apm import FunctionRegistry, FUNCTION
from typing import TypedDict, Literal
from uuid import getnode


class Server:
    class ServerFunctionRegistry(FunctionRegistry):
        EVENT = Literal["on_message", "on_client_connect"]

        def __call__(self, arg: EVENT | FUNCTION) -> FUNCTION | Callable[[FUNCTION], FUNCTION]:
            return super().__call__(arg)

    def __init__(self) -> None:
        self.running: bool = False

        self.socket: socket | None = None

        self.event = self.ServerFunctionRegistry()

    def start(self, port: int, backlog: int = 1):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        self.socket.bind(("0.0.0.0", port))
        self.socket.listen(backlog)

        self.running = True

        running_thread = Thread(target=self.keep_alive)
        running_thread.start()

        accept_thread = Thread(target=self.accept_clients, daemon=True)
        accept_thread.start()

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
            self.event.on_client_connect(client_socket)

            while self.running:
                raw_data = client_socket.recv(1024)

                if not raw_data:
                    break

                messages = decode_message(raw_data)

                for message in messages:
                    if not message["message"].strip():
                        break

                    self.event.on_message(client_socket, message)

    def __enter__(self) -> "Server":
        return self

    def __exit__(self, *_):
        self.stop()

    def __del__(self):
        self.stop()


def get_ip() -> str:
    return gethostbyname(gethostname())


class DecodedMessage(TypedDict):
    message: str
    encodeTime: datetime
    decodeTime: datetime
    macId: str


def decode_message(raw_data: bytes) -> list[DecodedMessage]:
    messages = raw_data.decode("utf-8").split("\x00")
    decoded_messages = []

    for m in messages:
        if not m:
            continue

        data = loads(m)

        data["encodeTime"] = datetime.fromisoformat(data["encodeTime"])
        data["decodeTime"] = datetime.now()

        decoded_messages.append(data)

    return decoded_messages


def encode_message(message: Any) -> bytes:
    data = {
        "message": message,
        "encodeTime": datetime.now().isoformat(),
        "macId": f"{getnode():012x}"
    }
    return f"{dumps(data)}\x00".encode("utf-8")


class Client:
    class ClientFunctionRegistry(FunctionRegistry):
        EVENT = Literal["on_message"]

        def __call__(self, arg: EVENT | FUNCTION) -> FUNCTION | Callable[[FUNCTION], FUNCTION]:
            return super().__call__(arg)
        
    def __init__(self):
        self.connected: bool = False

        self.socket: socket | None = None

        self.event = self.ClientFunctionRegistry()

    def connect(self, ip: str, port: int):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((ip, port))

        self.connected = True

        running_thread = Thread(target=self.keep_alive)
        running_thread.start()

        receive_thread = Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()

    def disconnect(self):
        if self.socket:
            self.connected = False
            self.socket.close()

    def send(self, message: str):
        if self.socket:
            data = encode_message(message)
            self.socket.send(data)

    def __del__(self):
        self.disconnect()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *_):
        self.disconnect()

    def receive_messages(self):
        if self.socket:
            while self.connected:
                raw_data = self.socket.recv(1024)

                if not raw_data:
                    break

                messages = decode_message(raw_data)

                for message in messages:
                    self.event.on_message(message)

    def keep_alive(self):
        while self.connected:
            sleep(1)


__all__ = ["Server", "decode_message", "encode_message", "Client"]

if __name__ == '__main__':
    from apm import clear_console

    clear_console()

    server = Server()

    @server.event
    def on_message(client_socket: socket, data: DecodedMessage):
        client_ip, client_port = client_socket.getpeername()
        address = f"{client_ip}:{client_port}"

        send_time = data["encodeTime"]

        print(f"[{send_time}] {address} | {data["message"]}")

    server.start(2542)
