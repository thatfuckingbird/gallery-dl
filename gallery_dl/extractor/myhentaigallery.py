# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://myhentaigallery.com/"""

from .common import GalleryExtractor
from .. import text, exception


class MyhentaigalleryGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from myhentaigallery.com"""
    category = "myhentaigallery"
    root = "https://myhentaigallery.com"
    directory_fmt = ("{category}", "{gallery_id} {artist:?[/] /J, }{title}")
    pattern = (r"(?:https?://)?myhentaigallery\.com"
               r"/gallery/(?:thumbnails|show)/(\d+)")
    example = "https://myhentaigallery.com/gallery/thumbnails/12345"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/gallery/thumbnails/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def _init(self):
        self.session.headers["Referer"] = self.gallery_url

    def metadata(self, page):
        extr = text.extract_from(page)
        split = text.split_html

        title = extr('<div class="comic-description">\n', '</h1>').lstrip()
        if title.startswith("<h1>"):
            title = title[len("<h1>"):]

        if not title:
            raise exception.NotFoundError("gallery")

        return {
            "title"     : text.unescape(title),
            "gallery_id": text.parse_int(self.gallery_id),
            "tags"      : split(extr('<div>\nCategories:', '</div>')),
            "artist"    : split(extr('<div>\nArtists:'   , '</div>')),
            "group"     : split(extr('<div>\nGroups:'    , '</div>')),
            "parodies"  : split(extr('<div>\nParodies:'  , '</div>')),
        }

    def images(self, page):
        return [
            (text.unescape(text.extr(url, 'src="', '"')).replace(
                "/thumbnail/", "/original/"), None)
            for url in text.extract_iter(page, 'class="comic-thumb"', '</div>')
        ]
