import contextlib
import sys
from pathlib import Path
from random import randint
from subprocess import Popen, TimeoutExpired

import pytest

from .sftpserver import ROOT


class Server:
    def __init__(self, *, port):
        self.port = port
        self.root = ROOT


@pytest.fixture(scope="session")
def server():
    port = randint(10000, 65535)
    log_path = Path(__file__).parent / "sftpserver.log"
    log_file = log_path.open("w")
    process = Popen(
        [sys.executable, "-um", "tests.sftpserver", "-p", str(port)],
        stdout=log_file,
        stderr=log_file,
    )
    with contextlib.suppress(TimeoutExpired):
        process.communicate(timeout=1)
    return Server(port=port)
