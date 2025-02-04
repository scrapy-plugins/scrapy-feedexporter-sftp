from __future__ import annotations

from io import StringIO
from posixpath import dirname
from typing import TYPE_CHECKING, Any, Self
from urllib.parse import unquote_plus, urlparse

from paramiko import RSAKey, SFTPClient, Transport
from scrapy.extensions.feedexport import BlockingFeedStorage

if TYPE_CHECKING:
    from scrapy.crawler import Crawler


def sftp_makedirs(sftp, path):
    """Creates the `path` directory and its parent directories if they do not
    exist. The `sftp` parameter must be an already connected and logged in
    paramiko.SFTPClient object.
    """
    path = path.rstrip("/")
    cwd = sftp.getcwd()  # Remember the current working dir
    try:
        sftp.chdir(path)
    except OSError:
        # Directory `path` does not exist yet.
        sftp_makedirs(sftp, dirname(path))  # Make parent directories
        sftp.mkdir(path)  # Make directory
    sftp.chdir(cwd)  # Restore the original working directory.


class SFTPFeedStorage(BlockingFeedStorage):
    def __init__(self, uri, feed_options=None, crawler=None):
        u = urlparse(uri)
        self.host = u.hostname
        self.port = int(u.port or "22")
        self.username = unquote_plus(u.username or "")
        self.password = unquote_plus(u.password or "")
        self.path = u.path
        if pkey := crawler.settings.get("FEED_STORAGE_SFTP_PKEY"):
            pkey = RSAKey.from_private_key(StringIO(pkey.strip()))
        self.pkey = pkey

    @classmethod
    def from_crawler(
        cls,
        crawler: Crawler,
        uri: str,
        *,
        feed_options: dict[str, Any] | None = None,
    ) -> Self:
        return cls(
            uri=uri,
            feed_options=feed_options,
            crawler=crawler,
        )

    def _store_in_thread(self, file):
        file.seek(0)
        transport = Transport((self.host, self.port))
        try:
            transport.connect(
                username=self.username, password=self.password, pkey=self.pkey
            )
            sftp = SFTPClient.from_transport(transport)
            try:
                sftp_makedirs(sftp, dirname(self.path))
                chunk_size = 1024**2
                with sftp.file(self.path, "w") as f:
                    while True:
                        data = file.read(chunk_size)
                        if not data:
                            break
                        f.write(data)
            finally:
                sftp.close()
        finally:
            transport.close()
