import json
import time
import socket
import struct
import structlog

from typing import (
    Union,
    Tuple
)

from dataclasses import dataclass

from repository.robot.robot import (
    RobotRepo
)

from repository.robot.schemas import (
    RobotInfo,
    RobotStatus
)

from helpers.time_helper import to_taipei_time

class ParseMessageError(BaseException):
    pass

@dataclass
class TcpServerSettings:
    ip: str
    port: int

class TCPServer:

    def __init__(self, 
                 logger: structlog.stdlib.BoundLogger,
                 robot_repo: RobotRepo):
        
        # register log handler
        self.logger = logger

        # register robot repo
        self._robot_repo = robot_repo

    def register_tcp_server(self,
                            tcp_server_settings: TcpServerSettings):

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket .setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket .bind((tcp_server_settings.ip, tcp_server_settings.port))
        self._server_socket.listen(1)  # Listen for one client at a time
        
        self.logger.info("[TCPServer][register_tcp_server] Register tcp server session")

    def parse_message(self, data: bytes) -> Tuple[str, str]:

        # resolve data
        try:
            start_pos = 0
            end_pos = 4

            # message name
            message_name_length = data[start_pos: end_pos]

            num, = struct.unpack("<I", message_name_length)

            start_pos = end_pos
            end_pos += num

            message_name = data[start_pos: end_pos].decode("utf-8")

            # data
            start_pos = end_pos
            end_pos += 4

            data_length = data[start_pos: end_pos]
            num, = struct.unpack("<I", data_length)
            
            start_pos = end_pos
            end_pos += num

            message = data[start_pos: end_pos].decode("utf-8")

        except Exception as err:
            self.logger.error("[TCPServer][parser_message] Failed to parse received message: s{}".format(err))
            raise ParseMessageError("Failed to parse received message")
        
        return (message_name, message)
    
    def handle_robot_info(self, message: str):

        try:
            message = json.loads(message)
            robot_info = RobotInfo(**message,
                                     registered_at=to_taipei_time(timestamp=time.time()))
            self._robot_repo.register(robot_info=robot_info)
        except Exception as err:
            self.logger.info("[TCPServer][handle_robot_info] Failed to register robot: {}".format(err))

    def handle_robot_status(self, message: str):

        try:
            message = json.loads(message)
            robot_status = RobotStatus(**message,
                                      registered_at=to_taipei_time(timestamp=time.time()),
                                      updated_at=to_taipei_time(timestamp=time.time()))
            self._robot_repo.upsert_robot_status(robot_status=robot_status)
        except Exception as err:
            self.logger.info("[TCPServer][handle_robot_status] Failed to loads robot status: {}".format(err))

    def listen(self):

        self._server_conn, addr = self._server_socket.accept()

        try:
            while True:
                data = self._server_conn.recv(1024)
                if not data:
                    break
                
                # parsing data which receive from tcp client
                try:
                    message_name, message  =self.parse_message(data=data)
                except Exception as err:
                    self.logger.error(f"{str(err)}")
                    self._server_conn.sendall("ACK".encode())
                    continue

                if message_name == "robot_info":
                    self.handle_robot_info(message=message)
                elif message_name == "robot_status":
                    self.handle_robot_status(message=message)

                self._server_conn.sendall("ACK".encode())

        except ConnectionRefusedError:
            self.logger.error("[TCPServer][listen] Client disconnected")

        self._server_conn.close()
        self._server_socket.close()

def setup_tcp_server(logger: structlog.stdlib.BoundLogger,
                     robot_repo: RobotRepo) -> TCPServer:

    tcp_server = TCPServer(logger=logger, robot_repo=robot_repo)
    tcp_server.register_tcp_server(tcp_server_settings=TcpServerSettings(ip="0.0.0.0", port=10000))

    return tcp_server