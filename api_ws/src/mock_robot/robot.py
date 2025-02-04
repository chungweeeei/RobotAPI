import json
import time
import struct
import socket
import structlog

from typing import (
    List
)

from dataclasses import (
    dataclass,
    asdict
)

@dataclass
class RobotStatus:
    robot_id: str
    map_id: str
    position_x: float
    position_y: float
    position_yaw: float

    def convert_to_bytes(self):

        # serialize data into LV type data
        try:
            topic_name_bytes = "robot_status".encode("utf-8")
            topic_name_len = len(topic_name_bytes)
            topic_name_message = struct.pack("<I%ss" % topic_name_len, topic_name_len, topic_name_bytes)

            robot_status = asdict(self)

            robot_status_bytes = json.dumps(robot_status).encode("utf-8")
            robot_status_len = len(robot_status_bytes)
            robot_status_message = struct.pack("<I%ss" % robot_status_len, robot_status_len, robot_status_bytes)

            serialized_data = topic_name_message + robot_status_message

        except Exception: 
            return b""
        
        return serialized_data

@dataclass
class RobotInfo:
    robot_id: str
    robot_name: str

    def convert_to_bytes(self):

        # serialize data into LV type data
        try:
            topic_name_bytes = "robot_info".encode("utf-8")
            topic_name_len = len(topic_name_bytes)
            topic_name_message = struct.pack("<I%ss" % topic_name_len, topic_name_len, topic_name_bytes)

            robot_status = asdict(self)

            robot_info_bytes = json.dumps(robot_status).encode("utf-8")
            robot_info_len = len(robot_info_bytes)
            robot_info_message = struct.pack("<I%ss" % robot_info_len, robot_info_len, robot_info_bytes)

            serialized_data = topic_name_message + robot_info_message

        except Exception: 
            return b""
        
        return serialized_data

class TCPClient:

    def __init__(self, logger: structlog.stdlib.BoundLogger):

        self.logger = logger

    def regsiter_tcp_session(self, ip: str, port: int):

        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._client_socket.connect((ip, port))
        except Exception as err:
            self.logger.error("[TCPClient][register_tcp_session] Failed to connect tcp server: {}".format(err))
            raise Exception("[TCPClient][register_tcp_session] Failed to connect tcp server")

    def send(self, messages: List):

        try:
            while True:
                for message in messages:
                    self._client_socket.sendall(message)
                response = self._client_socket.recv(1024).decode()
                self.logger.info("[TCPClient][send] Received from server: {}".format(response))

                time.sleep(5.0)
        except Exception as err:
            self.logger.error("[TCPClient][send] Failed to send heartbeat message: {}".format(err))
        finally:
            self._client_socket.close()


def setup_tcp_client(logger: structlog.stdlib.BoundLogger) -> TCPClient:

    tcp_client = TCPClient(logger=logger)

    return tcp_client

if __name__ == "__main__":

    tcp_client = setup_tcp_client(logger=structlog.get_logger())
    tcp_client.regsiter_tcp_session(ip="localhost", port=10000)

    robot_info = RobotInfo(robot_id="robot05", 
                           robot_name="05")
    robot_status = RobotStatus(robot_id="robot05",
                               map_id="123456",
                               position_x=5.0,
                               position_y=5.0,
                               position_yaw=5.0)

    tcp_client.send(messages=[robot_info.convert_to_bytes(), 
                              robot_status.convert_to_bytes()])

    