"""
PRECISA INSTALAR NET-TOOLS
sudo apt intall net-tools
NÃO tem hadshake, td mundo pode escutar, vc só fala quem vc quer q escute
"""

import logging
import os
import platform
import sys
from threading import Thread
from typing import Iterable

import cv2
import numpy as np
import zmq

from utils import Utils, show_text, show_video  # pylint: disable=E0401
from utils.constants import DATETIME_LOG_FORMAT, LOG_FORMAT

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(LOG_FORMAT, DATETIME_LOG_FORMAT)
file_handler = logging.FileHandler(f"{__name__}.log")
file_handler.setFormatter(formatter)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


DEFAULT_PORT = 5555
LISTEN_TOPIC_FILTERS = {
    # "broadcast": 0,
    "text": b"broadcast/text",
    "video": b"broadcast/video",
    "audio": b"broadcast/audio",
    # "logout": 1
}
LISTEN_TOPIC_ROUTINES = {
    b"broadcast/video": show_video,
    b"broadcast/text": show_text,
}

BROADCAST_TOPIC = b""


ZMQ_CONTEXT = zmq.Context()
SEND_SOCKET = ZMQ_CONTEXT.socket(zmq.PUB)  # pylint: disable=E1101
SEND_SOCKET.bind(f"tcp://*:{DEFAULT_PORT}")
RECIEVE_SOCKET = ZMQ_CONTEXT.socket(zmq.SUB)  # pylint: disable=E1101

LISTEN_THREADS = []


def recv_routine(name: str, ip: str, topic_filter: bytes):
    """
    Connects and recieves the data stream
    """

    endpoint = f"tcp://{ip}:{DEFAULT_PORT}"
    RECIEVE_SOCKET.connect(f"tcp://{ip}:{DEFAULT_PORT}")

    logger.info("connected to %s @ %s", name, endpoint)

    for topic in LISTEN_TOPIC_FILTERS.values():
        RECIEVE_SOCKET.setsockopt(zmq.SUBSCRIBE, topic)

    logger.info("subd")

    while True:
        msg = RECIEVE_SOCKET.recv()  # AQUI RECEBE, PRECISA STREAMAR FEED PRA TELA
        topic, payload = msg.split(b" ", maxsplit=1)

        # logger.info("rcvd from topic: '%s'; msg:'%s'", topic.decode("utf-8"), payload.decode("utf-8"))

        if topic == LISTEN_TOPIC_FILTERS["video"]:
            logger.info(".")
            frame_array = np.frombuffer(payload, dtype=np.uint8)  # Converte os bytes recebidos para um array NumPy
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)  # Decodifica o array para obter o frame

            cv2.imshow(name, frame) #exibe o frame recebido
            if cv2.waitKey(5) == 27: #pressiona esc para sair
                break
        
        else:
            logger.info(topic)
            LISTEN_TOPIC_ROUTINES[topic](payload)

    cv2.destroyAllWindows()

def broadcast_routine():
    """
    broadcasts video to anyone listening
    """

    id_ = 0 if platform.system() != "Darwin" else 1
    print(id_)

    webcam = cv2.VideoCapture(id_)
    while webcam.isOpened():
        validacao, frame = webcam.read()
        if not validacao:
            break
        encoded_frame = cv2.imencode('.webp', frame)[1]
        
        SEND_SOCKET.send(LISTEN_TOPIC_FILTERS["video"] + b" " + encoded_frame.tobytes()) #envia o frame em bytes
        
        if cv2.waitKey(5) == 27: #pressiona esc para sair
            break

    webcam.release() #encerra conexao com a webcam
    cv2.destroyAllWindows()


def main(*, desigred_dict: Iterable[str]):
    """
    main func loop
    """

    logger.info("rcv_usrs_dict : %s", desigred_dict)

    Thread(target=broadcast_routine).start()
    for name, ip in desigred_dict.items():  # só se conecta nos usuários que vc quer ouvir
        # TODO: fix topic_filter
        topic_filter = b""
        t = Thread(target=recv_routine, args=(name, ip, topic_filter))
        t.start()
        LISTEN_THREADS.append(t)


    # TESTS_TEXT:
    while msg := input():
        SEND_SOCKET.send(f"{LISTEN_TOPIC_FILTERS['text']} {msg}".encode("utf-8")) # AQUI ENVIA
        print("SENT!")

    

if __name__ == "__main__":

    # Utils.set_redis_for_tests()

    usr_tbl_dict = Utils.get_usrs_tbl()
    available_usrs = {
        str(i): usr_name for i, usr_name in enumerate(usr_tbl_dict.keys())
    }

    logger.info(available_usrs)

    VALID_USR_NAME = False
    while not VALID_USR_NAME:
        usr_name = input("Please type your username: ")

        if usr_name not in usr_tbl_dict.keys():
            VALID_USR_NAME = True
        else:
            print("INVALID USERNAME")

    Utils().announce_usr(usr_name)

    DESIGNRED_CONN = "-1"
    while DESIGNRED_CONN in ("-1", None, ""):

        usr_tbl_dict = Utils.get_usrs_tbl()
        available_usrs = {
            str(i): usr_name for i, usr_name in enumerate(usr_tbl_dict.keys())
        }
        os.system("cls||clear")
        print("Online users:")
        for k, v in available_usrs.items():
            print(f"\t{k}: {v}")

        DESIGNRED_CONN = input("Select the desigred usrs: (type IDs seperated by comma (','))\n(-1 to refresh):\n")

    desigred_conn_ids = []
    desigred_conn_ids = DESIGNRED_CONN.replace(" ", "").split(",")

    desigred_dict_input = {}
    for id_ in desigred_conn_ids:
        name_ = available_usrs[id_]
        desigred_dict_input[name_] = usr_tbl_dict[name_]

    # logger.info("desigred_dict: %s", desigred_dict_input)

    main(desigred_dict=desigred_dict_input)
