from logging import exception
from pathlib import Path
from shutil import Error
from typing import Tuple, List
import argparse
import errno
import os
import logging
import shutil
import click

logging.basicConfig(level=logging.DEBUG)


def dir_empty(dir_path):
    return not any([True for _ in os.scandir(dir_path)])


def get_path_depth(path: Path, depth: int = 0) -> List[Tuple[Path, int]]:

    result = [(path, depth)]
    for subPath in path.iterdir():
        if subPath.is_dir():
            result = result + get_path_depth(subPath, depth=depth + 1)
    return result


def create_aa_dict(path: Path, raise_error: bool = True, logfile=None) -> dict:
    result = get_path_depth(path)
    tooDeep = list(filter(lambda x: (x[1] > 2), result))
    if len(tooDeep) > 0:
        if logfile is not None:
            for dir in tooDeep:
                logfile.write(dir[0].as_posix())
        logging.error("Fount too deep Folder structure has to be artists/albumns")
        if raise_error is True:
            raise FileExistsError(tooDeep)
    sourceDict = {}

    new_albumns = list(filter(lambda x: (x[1] == 2), result))
    for albumnPath in new_albumns:
        pathParts = albumnPath[0].parts
        key = (pathParts[len(pathParts) - 2], pathParts[len(pathParts) - 1])
        sourceDict[key] = albumnPath
    return sourceDict


simulate = True

parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "source", metavar="path", type=Path, nargs=1, help="folder of new music"
)
parser.add_argument(
    "target", metavar="path", type=Path, nargs=1, help="folder of your libary"
)
parser.add_argument(
    "dups", metavar="path", type=Path, nargs=1, help="folder of your libary"
)

parser("dups", metavar="path", type=Path, nargs=1, help="folder of your libary")

args = parser.parse_args()
source: Path = args.source[0]
target: Path = args.target[0]
dups: Path = args.dups[0]


def main():
    with open("import_log.txt", "w+") as file:
        try:
            if source.exists() is False and source.is_dir():
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), source)
            if target.exists() is False and source.is_dir():
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), target)
            if dups.exists() is False and source.is_dir():
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dups)

            logging.info("Check if import folder has structure Alrtist/Albumns")
            sourceDict = create_aa_dict(source)
            libDict = create_aa_dict(target, raise_error=True, logfile=file)

            logging.info("Start moving folders")
            for key, path in sourceDict.items():
                if key in libDict:
                    continue
                # check if artist allready exists
                artist_folder = target / Path(key[0])
                if artist_folder.exists() is False:
                    if simulate:
                        os.mkdir(artist_folder)
                source_folder = source / Path(key[0]) / Path(key[1])
                target_folder = target / Path(key[0]) / Path(key[1])
                if simulate:
                    shutil.move(source_folder.as_posix(), target_folder.as_posix())

            logging.info("Remove empty folders")
            for artist in source.iterdir():
                if artist.is_dir():
                    if dir_empty(artist):
                        os.rmdir(artist)
        except:
            raise