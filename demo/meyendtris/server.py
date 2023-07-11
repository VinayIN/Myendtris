import zmq
import logging
from zmq.log.handlers import PUBHandler
import time
import sys
import inspect

logger = logging.getLogger("meyendtris")
logging.basicConfig(level=logging.INFO)

def exit_from_python():
    sys.exit("Exit command entered")

class Server:
    def __init__(self, host="*", port="18812", logger_port="18813", log=False):
        self.host = host
        self.port = port
        self.logger_port = logger_port
        self.log = log
        self._rep = None
        # {message_from_client_side: action_to_perform_on_server_side}
        # After the action is performed, return a string that needs to be replied on client side
        self.invoke_client_command = {
            "0": "command_mode",
            "start": None,
            "restart": None,
            "exit": exit_from_python}

        self._ctx = zmq.Context()
        if self.log:
            self._pub = self._ctx.socket(zmq.PUB)
            self._pub.bind(f'tcp://{self.host}:{self.logger_port}')
    
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
            logger.info(message)
            print("------")
            func = self.invoke_client_command.get(message, "")
            self.send_message(message=f"Running {func}")
            if inspect.isfunction(func):
                func()
            return f"Finished client's request for {message}"
        
        print("-------")
        self.send_message(message_client)
        return message

if __name__ == "__main__":
    server = Server(log=True)
    if server.log:
        handler = PUBHandler(server._pub)
        logger.addHandler(handler)
        time.sleep(0.1)
        logger.info("PUBHandler Logger initialised")
    message = server.receive_message(message_client="command_mode")
    logger.info(message)
    # Establish relationship with client, if any
    try:
        while True:
            message = server.receive_message()
            time.sleep(0.1)
            logger.info(message)
    except KeyboardInterrupt:
        print("exiting")