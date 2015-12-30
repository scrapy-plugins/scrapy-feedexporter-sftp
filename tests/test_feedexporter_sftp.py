import os
import unittest

from io import BytesIO
from scrapy import Spider
from scrapy.extensions.feedexport import IFeedStorage
from twisted.internet import defer
from zope.interface.verify import verifyObject

from scrapy_feedexporter_sftp import SFTPFeedStorage


class SFTPFeedStorageTest(unittest.TestCase):

    def test_store(self):
        uri = os.environ.get("FEEDTEST_SFTP_URI")
        path = os.environ.get("FEEDTEST_SFTP_PATH")
        if not (uri and path):
            raise unittest.SkipTest("No SFTP server available for testing")
        st = SFTPFeedStorage(uri)
        verifyObject(IFeedStorage, st)
        return self._assert_stores(st, path)

    @defer.inlineCallbacks
    def _assert_stores(self, storage, path):
        spider = Spider("default")
        file = storage.open(spider)
        file.write(b"content")
        yield storage.store(file)
        self.assertTrue(os.path.exists(path))
        with open(path, "rb") as fp:
            self.assertEqual(fp.read(), b"content")
        # again, to check files are overwritten
        yield storage.store(BytesIO(b"new content"))
        with open(path, "rb") as fp:
            self.assertEqual(fp.read(), b"new content")
