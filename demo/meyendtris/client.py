import zmq
import logging
import os

logging.basicConfig(level=logging.DEBUG)

class Client:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = "18812"
        self.log = True
        self._sub = None
        self._req = None

    def connect(self, request_reply: bool = False, pub_sub: bool = False):
        ctx = zmq.Context()
        if pub_sub:  
            sub = ctx.socket(zmq.SUB)
            sub.connect(f'tcp://{self.host}:{self.port}')
            return sub
        if request_reply:
            req = ctx.socket(zmq.REQ)
            req.connect(f'tcp://{self.host}:{self.port}')
            return req
        raise ValueError("Need a parameter to either connect to request_reply or pub_sub")
    

    def receive(self):
        self._req = self._req if isinstance(self._req, zmq.Socket) else self.connect(request_reply=True)
        message = self._req.recv_string()
        print(message)
        if message == "need_command":
            self.send()

    def send(self, ping=False):
        self._req = self._req if isinstance(self._req, zmq.Socket) else self.connect(request_reply=True)         
        if ping:
            self._req.send_string(f"Connected with {os.getlogin()}")
            return
        print("#\n"*4)
        cmd = input(">> Enter a command to send to server\n")
        self._req.send_string(cmd)
        self.receive()
        

    def sub_logger(self):
        self._sub = self._sub if self._sub else self.connect(pub_sub=True)
        self._sub.setsockopt(zmq.SUBSCRIBE, b"")
        level_name, message = self._sub.recv_multipart()
        level_name = level_name.decode('ascii').lower()
        message = message.decode('ascii')
        if message.endswith('\n'):
            # trim trailing newline, which will get appended again
            message = message[:-1]
        log = getattr(logging, level_name)
        log(message)


if __name__ == "__main__":
    client = Client()
    try:
        while True:
            # unit
            client.send(ping=True)
            client.receive()
    except KeyboardInterrupt:
        print("exiting")
