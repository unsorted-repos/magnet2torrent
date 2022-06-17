"""Converts a magnet link into a .torrent file."""
import logging
import os
import re

import requests
from cachetools import TTLCache, cached
from decouple import config
from torrents.clients import InternalClient


def convert_magnet2torrent(magnet_link: str, output_dir: str):
    """Converts a (valid) magnet link to a .torrent and stores that .torrent
    file into an output directory.

    :param magnet_link: A valid magnet link whose torrent will be fetched.
    :param output_dir: The path in which the torrent will be stored.
    """
    verify_magnet_link(magnet_link)
    verify_output_dir_exists(output_dir)
    print("Getting .torrent file.")
    logger = logging.getLogger("Monitor worker")
    client = InternalClient(logger, load_trackers(logger))

    client.magnet2torrent(magnet_link, output_dir)
    print("Got .torrent file, will terminate this function in a few seconds.")


def verify_magnet_link(magnet_link: str):
    """Throws error if the magnet link does not follow magnet link URI
    formatting conventions.

    :param magnet_link: magnet url that is being verified.
    """
    pattern = re.compile(r"magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{32}")
    result = pattern.match(magnet_link)
    if result is not None:
        print("Magnet link is valid!")
    else:
        raise Exception("Magnet link is invalid.")


def verify_output_dir_exists(output_dir: str):
    """Throws error if output path does not exist.

    :param output_dir: path to which .torrent file is outputted.
    """
    if os.path.exists(output_dir):
        print("Output path exists.")
    else:
        raise Exception("Output path does not exist.")


@cached(cache=TTLCache(maxsize=500, ttl=86400))
def load_trackers(logger):
    """Gets a list of trackers from some repository to search for the torrents.

    :param logger: Object used by InternalClient to tell the user what went
    different, if anything goes unexpected.
    """
    trackers_from = config(
        "trackers",
        "https://raw.githubusercontent.com/ngosang/trackerslist/master/"
        + "trackers_all.txt",
    )
    trackers = (
        requests.get(trackers_from).content.decode("utf8").split("\n\n")[:-1]
    )
    logger.info(f"{len(trackers)} trackers loaded.")
    return trackers


# Use the magnet link for the Ubuntu 22.04 OS.
ubuntu_magnet_link = (
    "magnet:?xt=urn:btih:FRVWQWGWDWUVIPKCGGTR3NFRZETEWBUF&dn="
    + "ubuntu-22.04-desktop-amd64.iso&xl=3654957056&tr.1=https%3A%2F%2Ftorrent"
    ".ubuntu.com%2Fannounce&tr.2=https%3A%2F%2Ftorrent.ubuntu.com%2Fannounce"
    + "&tr.3=https%3A%2F%2Fipv6.torrent.ubuntu.com%2Fannounce"
)

# Specify an output dir
torrent_output_dir = "/home/name"

convert_magnet2torrent(ubuntu_magnet_link, torrent_output_dir)
