from typing import Any, Callable, TypeVar, ParamSpec


P = ParamSpec("P")
R = TypeVar("R")


class FunctionRegistry:
    def __init__(self):
        self.events: dict[str, Callable[..., object]] = {}
        self._pending_name: str | None = None

    def __call__(self, arg: str | Callable[..., object]) -> Callable[..., object] | Callable[[Callable[..., object]], Callable[..., object]]:
        if isinstance(arg, str):
            self._pending_name = arg
            return self
        else:
            func = arg
            name = self._pending_name or func.__name__
            self.events[name] = func
            self._pending_name = None
            return func

    def __getattr__(self, name: str) -> Callable[..., object]:
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


__all__ = ["FunctionRegistry"]


if __name__ == '__main__':
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
