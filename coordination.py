# wait/notify
from abc import ABC, abstractmethod
from typing import Any
import threading
import queue

condition = threading.Condition()

condition_met = False

with condition:
    while not condition_met:
        condition.wait()
    # do_work()
    condition.notify_all()


# Thread safe task scheduler, this uses wait/notify premitives [Blocking Queue]
class TaskScheduler:
    def __init__(self) -> None:
        self._q = queue.Queue(1000)

    def submit_task(self, task: callable) -> None:
        self._q.put(task)  # Blocks, if queue full

    def worker_loop(self) -> None:
        while True:
            try:
                task = self._q.get()  # blocks, if queue empty
                task()
            except queue.ShutDown:  # InterruptedException
                break


# Graceful shutdown
"""
for graceful shutdown we can use 3 approaches.
 - on shutdown we will receive Shutdown exception on the workers blocked on get, we can handle this exception and break out of the loop.
 - poison pill: send a special sentinel task, worker keeps processing normal tasks when it encounters poison pill it exits the loop.
 
"""

# Mesage passing co-ordination
"""
No shared state, each Actor has its own state and processes its messages sequentially
"""


class Actor(ABC):
    def __init__(self) -> None:
        self.mailbox = queue.Queue(1000)
        self.thread = threading.Thread(target=self._run)
        self.running = True
        self.thread.start()

    def _run(self):
        while True:
            try:
                message = self.mailbox.get(timeout=0.1)
                self.on_receive(message)
            except queue.Empty:
                continue

    def send(self, message: Any) -> None:
        self.mailbox.put(message)

    @abstractmethod
    def on_receive(self, message: Any) -> None:
        pass

    def stop(self):
        self.running = False
        self.thread.join()


class EmailClient:
    def send(self, to: str, subject: str, body: str):
        pass


class EmailActor(Actor):
    def __init__(self) -> None:
        super().__init__()
        self.email_client = EmailClient()

    def on_receive(self, message: Any) -> None:
        self.email_client.send(message.to, message.subject, message.body)


class User:
    pass


class EmailRequest:
    to: str
    subject: str
    body: str


# Usage


class SignupHandler:
    def __init__(self, user_repo) -> None:
        self.email_actor = EmailActor()
        self.user_repo = user_repo

    def handle_signup(self, request):
        user = self.user_repo.save(User(request.email))
        self.email_actor.send(
            EmailRequest(
                to=user.email, subject="welcome", body="Thanks for signing up..."
            )
        )
