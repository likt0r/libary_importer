from logging import exception
from pathlib import Path
from shutil import Error
import shutil
from typing import Tuple, List
import argparse
import errno
import os
from mimetypes import MimeTypes

mime = MimeTypes()


def check_true_then_false(booleans):
    return booleans == sorted(booleans, reverse=True)


def recursive_scan(path: Path) -> bool:
    results = []
    for x in os.scandir(path):
        file = path.joinpath(x)
        if file.is_dir():
            if recursive_scan(file):
                results.append(True)
            else:
                print("delete: " + file.as_posix())
                shutil.rmtree(file)

    if len(results) == 0:
        for x in os.scandir(path):
            file = path.joinpath(x)
            filename = "{}{}".format(file.name, file.suffix)
            mime_type = mime.guess_type(filename)
            if mime_type[0] is not None and (
                mime_type[0].startswith("audio") or file.suffix == ".mpc"
            ):
                return True
        return False
    return True


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "source", metavar="path", type=Path, nargs=1, help="folder of new music"
)

args = parser.parse_args()
source: Path = args.source[0]
if source.exists() is False and source.is_dir():
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), source)
recursive_scan(source)