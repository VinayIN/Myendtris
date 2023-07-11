import zmq
import logging
from zmq.log.handlers import PUBHandler

logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)


class Server:
    def __init__(self):
        self.host = "*"
        self.port = "18812"
        self.log = False
        self._rep = None

        self._ctx = zmq.Context()
        if self.log:
            self._pub = self._ctx.socket(zmq.PUB)
            print('tcp://{self.host}:{self.port}')
            self._pub.bind("tcp://*:5555")
            handler: PUBHandler = PUBHandler(self._pub)
            logger.addHandler(handler)
    
    def get_connection(self):
        req = self._ctx.socket(zmq.REP)
        req.bind(f'tcp://{self.host}:{self.port}')
        return req
    
    def send_message(self, message: str):
        self._rep = self._rep if isinstance(self._rep, zmq.Socket) else self.get_connection()
        self._rep.send_string(message)
    
    def receive_message(self):
        self._rep = self._rep if isinstance(self._rep, zmq.Socket) else self.get_connection()
        message = self._rep.recv_string()
        return message

if __name__ == "__main__":
    server = Server()
    try:
        while True:
            # unit 
            message = server.receive_message()
            print(message)
            message = input("Enter your message\n")
            server.send_message(message=message)
    except KeyboardInterrupt:
        print("exiting")
    
        