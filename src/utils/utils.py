import os
import platform
import socket
import subprocess
from threading import Thread
from time import sleep
from typing import Any, Iterable, Mapping

from dotenv import load_dotenv
from redis import Redis

load_dotenv()
currentdir = os.path.dirname(os.path.realpath(__file__))

REDIS_USR_KEY_PREFIX = "usr:"
REDIS_USR_KEY_PATTERN = f"{REDIS_USR_KEY_PREFIX}*"
REDIS_TIMEOUT_SECONDS = 10

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", "17740"))
REDIS_PASS = os.getenv("REDIS_PASS")


GET_IP_COMDS = {
    "Windows": "ifconfig | grep \"inet \" | grep -Fv 127.0.0.1 | awk '{print $2}' ",
    "Darwin": "ifconfig | grep \"inet \" | grep -Fv 127.0.0.1 | awk '{print $2}' ",
    "Linux": ""
}


class Utils:
    """
    General Utils for Module
    """
    
    @staticmethod
    def get_usrs_tbl() -> Mapping[str, str]:
        """
        [PLACEHOLDER]: SUBSTITUTE WITH REDIS

        Returns:
            {
                "USR_NAME_0": "$USR_0_IP,
                "USR_NAME_1": "$USR_1_IP,
                "USR_NAME_2": "$USR_2_IP,
                ...
            }
        """

        # with open(os.path.join(currentdir, "tbl.json"), mode="r", encoding="utf-8") as file:
        #     return json.load(file)

        redis = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
        keys = redis.keys(REDIS_USR_KEY_PATTERN)

        return {
            k[len(REDIS_USR_KEY_PATTERN) - 1:].decode('utf-8'): redis.get(k).decode('utf-8') for k in keys
        }

    @staticmethod
    def fix_k_v(d: Mapping[Any, Any], /) -> Iterable[Mapping[str, Any]]:
        """
        Fix the "dict keys should not contain information" problem
        """

        nw_lst = []
        for k, v in d.items():
            nw_lst.append({
                "key": k,
                "value": v
            })

        return nw_lst

    @staticmethod
    def get_ip() -> str:
        """
        gets own local (private) ip
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        except Exception:  # pylint: disable=W0718
            cmd = GET_IP_COMDS[platform.system()]

            ip = subprocess.run(["/bin/sh", "-c", cmd], stdout=subprocess.PIPE).stdout[:-1].decode('utf-8')
        finally:
            s.close()
        return ip

    @staticmethod
    def announce_usr(usr_name: str, /):
        """
        Announces the usr on redis
        """

        def set_ip_routine():
            """
            Routine to set up in loop
            """

            while True:
                local_ip = Utils.get_ip()

                redis = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
                redis.setex(
                    name=f"{REDIS_USR_KEY_PREFIX}{usr_name}",
                    time=REDIS_TIMEOUT_SECONDS,
                    value=local_ip
                )

                sleep(REDIS_TIMEOUT_SECONDS - 1)

        Thread(target=set_ip_routine).start()

    @staticmethod
    def set_redis_for_tests():
        """
        """

        from faker import Faker

        Faker.seed(42)
        fake = Faker("pt-BR")

        redis = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
        for _ in range(10):
            name = fake.name()
            val = fake.ipv4()
            redis.set(name=f"{REDIS_USR_KEY_PREFIX}{name}", value=val)
