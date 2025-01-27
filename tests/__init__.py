try:
    from scrapy.utils.misc import build_from_crawler
except ImportError:  # Scrapy < 2.12
    from typing import Any, TypeVar

    from scrapy.crawler import Crawler
    from scrapy.utils.misc import create_instance

    T = TypeVar("T")

    def build_from_crawler(
        objcls: type[T], crawler: Crawler, /, *args: Any, **kwargs: Any
    ) -> T:
        return create_instance(objcls, None, crawler, *args, **kwargs)
