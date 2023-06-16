"""
NÃO tem hadshake, td mundo pode escutar, vc só fala quem vc quer q escute
"""

import logging
import sys
from typing import Iterable

import zmq

from utils import Utils  # pylint: disable=E0401
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
    "broadcast": 0,
    "logout": 1
} # must be int - not unicode


def main(*, desigred_dict: Iterable[str]):
    """
    main func loop
    """
    

    logger.info("rcv_usrs_dict : %s", desigred_dict)

    zmq_context = zmq.Context()
    snd_socket = zmq_context.socket(zmq.PUB)  # pylint: disable=E1101
    snd_socket.bind(f"tcp://*:{DEFAULT_PORT}")
    rcv_socket = zmq_context.socket(zmq.SUB)  # pylint: disable=E1101

    for ip in desigred_dict.values():  # só se conecta nos usuários que vc quer ouvir
        rcv_socket.connect(f"tcp://{ip}:{DEFAULT_PORT}")

    for val in LISTEN_TOPIC_FILTERS.values():
        rcv_socket.setsockopt(zmq.SUBSCRIBE, val)  # pylint: disable=E1101


if __name__ == "__main__":

    Utils.set_redis_for_tests()

    usr_tbl_dict = Utils.get_usrs_tbl()
    available_usrs = {
        str(i): usr_name for i, usr_name in enumerate(usr_tbl_dict.keys())
    }

    logger.info(available_usrs)

    VALID_USR_NAME = False
    while not VALID_USR_NAME:
        usr_name = input("please type your username: ")

        if usr_name not in usr_tbl_dict.keys():
            VALID_USR_NAME = True
        else:
            print("INVALID USERNAME")

    Utils().announce_usr(usr_name)

    DESIGNRED_CONN = "-1"
    while DESIGNRED_CONN == "-1":
        for k, v in available_usrs.items():
            print(f"\t{k}: {v}")

        DESIGNRED_CONN = input("Select the desigred usrs: (type IDs seperated by comma (','))\n(-1 to refresh):\n") #.replace(" ", "").split(",")

    desigred_conn_ids = []
    desigred_conn_ids = DESIGNRED_CONN.replace(" ", "").split(",")

    desigred_dict_input = {}
    for id_ in desigred_conn_ids:
        name = available_usrs[id_]
        desigred_dict_input[name] = usr_tbl_dict[name]

    logger.info("desigred_dict: %s", desigred_dict_input)

    main(desigred_dict=desigred_dict_input)