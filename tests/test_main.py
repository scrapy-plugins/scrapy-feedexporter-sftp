from io import BytesIO
from pathlib import Path

import pytest
from paramiko.ssh_exception import AuthenticationException
from pytest_twisted import ensureDeferred
from scrapy import Spider
from scrapy.extensions.feedexport import IFeedStorage
from scrapy.utils.test import get_crawler
from zope.interface.verify import verifyObject

from scrapy_feedexporter_sftp import SFTPFeedStorage

from . import build_from_crawler

TESTS_DIR = Path(__file__).parent
BAD_KEY = (TESTS_DIR / "bad_key").read_text()
GOOD_KEY = (TESTS_DIR / "good_key").read_text()


def humanize_arg_ids(value):
    if value == BAD_KEY:
        return "badkey"
    if value == GOOD_KEY:
        return "goodkey"
    return value


@pytest.mark.parametrize(
    ("username", "password", "private_key", "exception"),
    (
        ("username", "password", None, None),
        ("badusername", "password", None, AuthenticationException),
        (None, "password", None, AuthenticationException),
        ("username", "badpassword", None, AuthenticationException),
        ("username", None, None, AuthenticationException),
        ("badusername", "badpassword", None, AuthenticationException),
        (None, None, None, AuthenticationException),
        # If a good key is provided, the username is taken into account, but
        # the password has no effect.
        ("username", "password", GOOD_KEY, None),
        ("badusername", "password", GOOD_KEY, AuthenticationException),
        (None, "password", GOOD_KEY, AuthenticationException),
        ("username", "badpassword", GOOD_KEY, None),
        ("badusername", "badpassword", GOOD_KEY, AuthenticationException),
        (None, "badpassword", GOOD_KEY, AuthenticationException),
        (None, None, GOOD_KEY, AuthenticationException),
        # If a bad key is provided, even a good password will not get a
        # successful authentication.
        ("username", "password", BAD_KEY, AuthenticationException),
        ("badusername", "password", BAD_KEY, AuthenticationException),
        (None, "password", BAD_KEY, AuthenticationException),
        ("username", "badpassword", BAD_KEY, AuthenticationException),
        ("badusername", "badpassword", BAD_KEY, AuthenticationException),
        (None, "badpassword", BAD_KEY, AuthenticationException),
        (None, None, BAD_KEY, AuthenticationException),
    ),
    ids=humanize_arg_ids,
)
@ensureDeferred
async def test_auth(username, password, private_key, exception, server):
    settings = {}
    if private_key is not None:
        settings["FEED_STORAGE_SFTP_PKEY"] = private_key
    crawler = get_crawler(settings_dict=settings, spidercls=Spider)
    spider = Spider("default")
    spider.crawler = crawler

    file_name = "file.txt"
    username = username or ""
    password = f":{password}" if password is not None else ""
    storage = build_from_crawler(
        SFTPFeedStorage,
        crawler,
        f"sftp://{username}{password}@localhost:{server.port}/{file_name}",
    )
    verifyObject(IFeedStorage, storage)

    file = storage.open(spider)
    file.write(b"content")

    fs_file = server.root / file_name
    assert not fs_file.exists()

    if exception:
        with pytest.raises(exception):
            await storage.store(file)
        assert not fs_file.exists()
    else:
        await storage.store(file)
        assert fs_file.read_bytes() == b"content"
        fs_file.unlink()


@ensureDeferred
async def test_store(server):
    crawler = get_crawler(spidercls=Spider)
    spider = Spider("default")
    spider.crawler = crawler

    file_name = "file.txt"

    storage = build_from_crawler(
        SFTPFeedStorage,
        crawler,
        f"sftp://username:password@localhost:{server.port}/{file_name}",
    )
    verifyObject(IFeedStorage, storage)

    file = storage.open(spider)
    file.write(b"content")

    fs_file = server.root / file_name
    assert not fs_file.exists()

    await storage.store(file)
    assert fs_file.read_bytes() == b"content"

    await storage.store(BytesIO(b"overwritten content"))
    assert fs_file.read_bytes() == b"overwritten content"

    fs_file.unlink()
