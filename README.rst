========================
scrapy-feedexporter-sftp
========================

.. image:: https://img.shields.io/pypi/v/scrapy-feedexporter-sftp.svg
   :target: https://pypi.python.org/pypi/scrapy-feedexporter-sftp
   :alt: PyPI Version

.. image:: https://img.shields.io/github/license/scrapy-plugins/scrapy-feedexporter-sftp.svg
   :target: https://github.com/scrapy-plugins/scrapy-feedexporter-sftp/blob/master/LICENSE
   :alt: License


scrapy-feedexporter-sftp is a `Scrapy Feed Exporter Storage Backend
<http://doc.scrapy.org/en/latest/topics/feed-exports.html#storage-backends>`_
that allows you to export `Scrapy items
<http://doc.scrapy.org/en/latest/topics/items.html>`_ to an SFTP server.

Using scrapy-feedexporter-sftp
==============================

Add a ``FEED_STORAGES`` to your Scrapy settings:

.. code-block:: python

    FEED_STORAGES = {"sftp": "scrapy_feedexporter_sftp.SFTPFeedStorage"}

Define your ``FEED_URI`` in Scrapy settings:

.. code-block:: python

    FEED_URI = "sftp://user:password@some.server/some/path/to/a/file"

To use a private key for authentication, use the ``FEED_STORAGE_SFTP_PKEY``
setting:

.. code-block:: python

    FEED_STORAGE_SFTP_PKEY = """
    -----BEGIN RSA PRIVATE KEY-----
    ...
    ... base64 encoded ...
    ...
    -----END RSA PRIVATE KEY-----
    """
