==================================
scrapy-feedexporter-sftp changelog
==================================

1.1.0 (2025-02-12)
==================

-   Dropped support for Python 3.8 and lower, added support for Python 3.9 and
    higher.

-   Added a dependency on ``typing-extensions 3.6.2+`` on Python 3.10 and
    lower.

-   | Changed minimum versions of dependencies:
    | ``paramiko``: ``1.16.0`` → ``2.10.0``
    | ``scrapy``: ``1.0.3`` → ``2.0.0``

-   Added a new ``FEED_STORAGE_SFTP_PKEY`` setting, which allows connecting to
    an SFTP server using a private key instead of a password.

-   Added Scrapy 2.12+ support.


Earlier releases
================

Find the earlier commit history `at GitHub
<https://github.com/scrapy-plugins/scrapy-feedexporter-sftp/commits/054f095bcf34a2768c64e1119375d1d8a9011dd5/>`_.