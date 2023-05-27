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
        # {message_from_client_side: action_to_perform_on_server_side}
        # After the action is performed, return a string that needs to be replied on client side
        self.invoke_client_command = {
            "0": "command_mode",
            "start": None,
            "restart": None,
            "exit": None}

        self._ctx = zmq.Context()
        if self.log:
            self._pub = self._ctx.socket(zmq.PUB)
            self._pub.setsockopt(zmq.LINGER, 0)
            print('tcp://{self.host}:{self.port}')
            self._pub.bind("tcp://*:5555")
            handler: PUBHandler = PUBHandler(self._pub)
            logger.addHandler(handler)
    
    def get_connection(self):
        req = self._ctx.socket(zmq.REP)
        req.setsockopt(zmq.LINGER, 0)
        req.bind(f'tcp://{self.host}:{self.port}')
        return req
    
    def send_message(self, message: str):
        self._rep = self._rep if isinstance(self._rep, zmq.Socket) else self.get_connection()
        self._rep.send_string(f"Server: {message}")
    
    def receive_message(self, message_client="ack"):
        self._rep = self._rep if isinstance(self._rep, zmq.Socket) else self.get_connection()
        message = self._rep.recv_string()

        if message in self.invoke_client_command:
            # Check the message received and perform an operation
            print(message)
            print("------")
            self.send_message(message=self.invoke_client_command.get(message, ""))
            return f"Finished client's request for {message}"
        
        print("-------")
        self.send_message(message_client)
        return message

if __name__ == "__main__":
    server = Server()
    message = server.receive_message(message_client="command_mode")
    # Establish relationship with client, if any
    try:
        while True:
            message = server.receive_message()
            print(message)
    except KeyboardInterrupt:
        print("exiting")