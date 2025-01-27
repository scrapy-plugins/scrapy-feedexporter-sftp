from io import BytesIO
from logging import getLogger
from pathlib import Path
from subprocess import TimeoutExpired

from pytest_twisted import ensureDeferred
from scrapy import Spider
from scrapy.extensions.feedexport import IFeedStorage
from scrapy.utils.test import get_crawler
from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyObject

from scrapy_feedexporter_sftp import SFTPFeedStorage

from . import build_from_crawler

logger = getLogger(__name__)


class SFTPFeedStorageTest(TestCase):
    def log_stderr(self):
        try:
            out, err = self.process.communicate(timeout=1)
        except TimeoutExpired:
            pass
        else:
            if err := err.decode():
                for line in err.split("\n"):
                    logger.error(f"SFTP server (stderr): {line}")

    def setUp(self):
        self.port = 2225
        # self.port = randint(10000, 65535)
        # self.process = Popen(
        #     [sys.executable, "-um", "tests.sftpserver", "-p", str(self.port)],
        #     stderr=PIPE,
        # )
        # self.log_stderr()

    #
    # def tearDown(self):
    #     self.process.kill()
    #     self.log_stderr()

    @ensureDeferred
    async def test_client(self):
        from logging import getLogger

        from paramiko import SFTPClient, Transport

        logger = getLogger(__name__)

        import paramiko

        paramiko.util.log_to_file("paramiko.log")

        transport = Transport(("localhost", 2225), strict_kex=False)
        transport.connect(username="username", password="password")
        logger.error(f"sftp = SFTPClient.from_transport({transport=})")
        SFTPClient.from_transport(transport)

    @ensureDeferred
    async def test_store(self):
        file_name = "file.txt"
        crawler = get_crawler(spidercls=Spider)
        storage = build_from_crawler(
            SFTPFeedStorage,
            crawler,
            f"sftp://user:password@localhost:{self.port}/{file_name}",
        )

        verifyObject(IFeedStorage, storage)

        path = Path(file_name)
        spider = Spider("default")
        spider.crawler = crawler

        file = storage.open(spider)
        file.write(b"content")
        await storage.store(file)
        self.assertTrue(path.exists())
        with path.open("rb") as fp:
            self.assertEqual(fp.read(), b"content")

        # again, to check files are overwritten
        await storage.store(BytesIO(b"new content"))
        with path.open("rb") as fp:
            self.assertEqual(fp.read(), b"new content")
