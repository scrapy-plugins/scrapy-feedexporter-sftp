from posixpath import dirname
from urllib.parse import unquote_plus, urlparse

from paramiko import SFTPClient, Transport
from scrapy.extensions.feedexport import BlockingFeedStorage


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
    def __init__(self, uri, feed_options=None):
        u = urlparse(uri)
        self.host = u.hostname
        self.port = int(u.port or "22")
        self.username = unquote_plus(u.username)
        self.password = unquote_plus(u.password)
        self.path = u.path

    def _store_in_thread(self, file):
        file.seek(0)
        transport = Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)
        sftp = SFTPClient.from_transport(transport)

        sftp_makedirs(sftp, dirname(self.path))
        chunk_size = 1024**2
        with sftp.file(self.path, "w") as f:
            while True:
                data = file.read(chunk_size)
                if not data:
                    break
                f.write(data)
        sftp.close()
        transport.close()
