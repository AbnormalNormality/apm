# FunctionRegistry
```
from apm import FunctionRegistry


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
```