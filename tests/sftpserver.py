import os
import socket
from argparse import ArgumentParser
from pathlib import Path

from paramiko import (
    AUTH_SUCCESSFUL,
    OPEN_SUCCEEDED,
    RSAKey,
    ServerInterface,
    SFTPAttributes,
    SFTPHandle,
    SFTPServer,
    SFTPServerInterface,
    Transport,
)

ROOT = Path(__file__).parent / "fs"


class CustomSFTPServer(SFTPServerInterface):
    def _fs_path(self, path):
        return ROOT / path.lstrip("/")

    def stat(self, path):
        """Return dir st_mode if no file extension is included."""
        path = self._fs_path(path)
        return SFTPAttributes.from_stat(path.stat())

    def open(self, path, flags, attr):
        path = self._fs_path(path)
        try:
            binary_flag = getattr(os, "O_BINARY", 0)
            flags |= binary_flag
            mode = getattr(attr, "st_mode", None) or 0o666
            fd = os.open(path, flags, mode)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        if (flags & os.O_CREAT) and (attr is not None):
            attr._flags &= ~attr.FLAG_PERMISSIONS
            SFTPServer.set_file_attr(path, attr)
        if flags & os.O_WRONLY:
            fstr = "ab" if flags & os.O_APPEND else "wb"
        elif flags & os.O_RDWR:
            fstr = "a+b" if flags & os.O_APPEND else "r+b"
        else:
            fstr = "rb"
        try:
            f = os.fdopen(fd, fstr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        fobj = SFTPHandle(flags)
        fobj.filename = path
        fobj.readfile = f
        fobj.writefile = f
        return fobj


class CustomServer(ServerInterface):
    def check_auth_password(self, username, password):
        return AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        return OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"


def setup_transport(connection):
    transport = Transport(connection)
    transport.add_server_key(RSAKey.generate(bits=1024))
    transport.set_subsystem_handler("sftp", SFTPServer, CustomSFTPServer)
    transport.start_server(server=CustomServer())
    return transport


def main():
    parser = ArgumentParser()
    parser.add_argument("-p", "--port")
    args = parser.parse_args()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server_socket.bind(("localhost", int(args.port)))
    server_socket.listen()

    channels = []
    while True:
        connection, _ = server_socket.accept()
        transport = setup_transport(connection)
        channel = transport.accept()
        if not channel:
            continue
        channels[:] = [c for c in channels if not c.eof_received and not c.closed]
        channels.append(channel)


if __name__ == "__main__":
    main()
