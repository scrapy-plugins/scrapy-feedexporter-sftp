import contextlib
import sys
from io import BytesIO
from logging import getLogger
from random import randint
from subprocess import Popen, TimeoutExpired

from pytest_twisted import ensureDeferred
from scrapy import Spider
from scrapy.extensions.feedexport import IFeedStorage
from scrapy.utils.test import get_crawler
from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyObject

from scrapy_feedexporter_sftp import SFTPFeedStorage

from . import build_from_crawler
from .sftpserver import ROOT

logger = getLogger(__name__)


class SFTPFeedStorageTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.port = randint(10000, 65535)
        process = Popen(
            [sys.executable, "-um", "tests.sftpserver", "-p", str(cls.port)],
        )
        with contextlib.suppress(TimeoutExpired):
            process.communicate(timeout=1)

    @ensureDeferred
    async def test_store(self):
        crawler = get_crawler(spidercls=Spider)
        spider = Spider("default")
        spider.crawler = crawler

        file_name = "file.txt"

        storage = build_from_crawler(
            SFTPFeedStorage,
            crawler,
            f"sftp://user:password@localhost:{self.port}/{file_name}",
        )
        verifyObject(IFeedStorage, storage)

        file = storage.open(spider)
        file.write(b"content")

        fs_file = ROOT / file_name
        assert not fs_file.exists()

        await storage.store(file)
        assert fs_file.read_bytes() == b"content"

        await storage.store(BytesIO(b"overwritten content"))
        assert fs_file.read_bytes() == b"overwritten content"

        fs_file.unlink()
