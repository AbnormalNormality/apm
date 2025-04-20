# FunctionRegistry
```
class Mailbox:
    def __init__(self):
        self.event = FunctionRegistry()


mailbox = Mailbox()


@mailbox.event
def on_message(message: str):
    print(message)


mailbox.event.on_message("Hello, World!")
```