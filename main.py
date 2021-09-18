import os
import time
import asyncio
from typing import List, Optional
import urllib.parse
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

import fire
import requests
from bs4 import BeautifulSoup
from content_types import content_types_allowed


def _download(
        response: requests.Response,
):
    # TODO
    pass


def _parse(
        response: requests.Response,
        url_parsed: urllib.parse.ParseResult,
        outer_urls: bool,
) -> List[str]:
    # Content parser
    parser = BeautifulSoup(response.content, 'html.parser')

    urls = []

    # Get urls from attributes
    [urls.append(tag.get('href')) for tag in parser(href=True)]
    [urls.append(tag.get('src')) for tag in parser(src=True)]

    # Validate urls
    urls = [f'{url_parsed.scheme}://{url_parsed.netloc}{url}' if not urlparse(url).netloc else url for url in urls]
    urls = [url for url in urls if outer_urls or url_parsed.netloc == urlparse(url).netloc]

    return urls


def scrape(
        url: str,
        outer_urls: bool = False,
        content_types: List[str] = content_types_allowed,
        url_parsed: Optional[urllib.parse.ParseResult] = None,
):
    url_parsed = urlparse(url) if url_parsed is None else url_parsed

    # Url request
    response = requests.get(url)

    # Response type
    content_type = response.headers.get('content-type')

    # Response if file
    if content_type in content_types:
        return _download(response)

    # Response is not site
    if content_type.find('text/html') == -1:
        return

    # Get new urls
    urls = _parse(response, url_parsed, outer_urls)

    return [scrape(url, outer_urls, content_types, url_parsed) for url in urls]


if __name__ == '__main__':
    scrape(
        'https://vk.com'
    )
