from typing import Any, Callable, TypeVar, ParamSpec
from os import system
from sys import platform


P = ParamSpec("P")
R = TypeVar("R")

FUNCTION = Callable[..., object]


class FunctionRegistry:
    def __init__(self):
        self.events: dict[str, FUNCTION] = {}
        self._pending_name: str | None = None

    def __call__(self, arg: str | FUNCTION) -> FUNCTION | Callable[[FUNCTION], FUNCTION]:
        if isinstance(arg, str):
            self._pending_name = arg
            return self
        else:
            func = arg
            name = self._pending_name or func.__name__
            self.events[name] = func
            self._pending_name = None
            return func

    def __getattr__(self, name: str) -> FUNCTION:
        if name in self.__dict__:
            return self.__dict__[name]

        elif name in self.events:
            return self.events[name]

        else:
            return self._DefaultFunction()

    class _DefaultFunction:
        def __call__(self, *args: Any, **kwds: Any):
            return None

        def __bool__(self) -> bool:
            return False


def clear_console():
    if platform.startswith("linux") or platform == "darwin":
        system("clear")
        
    elif platform.startswith("win"):
        system("cls")


__all__ = ["FunctionRegistry", "clear_console", "FUNCTION"]


if __name__ == '__main__':
    clear_console()

    class Mailbox:
        def __init__(self):
            self.event = FunctionRegistry()

    mailbox = Mailbox()

    @mailbox.event
    def on_mail(message: str):
        print(message)

    on_mail_event = mailbox.event.on_mail
    if on_mail_event:
        on_mail_event("Hello, World!")

    @mailbox.event("on_spam")
    def spam_handler():
        return False

    mailbox.event.on_spam()
