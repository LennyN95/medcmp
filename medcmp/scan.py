import os
import hashlib
from enum import Enum
from medcmp.Report import Report

from typing import Optional


class FileType(Enum):
    RAW = "raw"
    DATA = "data"
    LABELMAP = "labelmap"


class Item:
    base: Optional[str] = None
    path: Optional[str] = None
    name: Optional[str] = None
    size: Optional[int] = None
    type: Optional[FileType] = None

    @property
    def relpath(self) -> str:
        assert self.path is not None
        return os.path.relpath(self.path, self.base)

    @property
    def hash(self) -> str:
        hstr = f"{len(self.relpath)}||{self.relpath}||{self.size}"
        return hashlib.md5(hstr.encode()).hexdigest()


def scan_tree(base: str):
    """
    Scan a directory into a list of files and extract file metadata.
    """

    # collect a list of file items
    items = {}

    # recursively iterate folder under path
    for root, _, files in os.walk(base):
        for name in files:
            # get full path
            path = os.path.join(root, name)

            # get file size
            size = os.path.getsize(path)

            # create a new item
            item = Item()
            item.base = base
            item.path = path
            item.name = name
            item.size = size

            # add to list
            items[item.relpath] = item

    # return results
    return items


def compare_tree_structures(src: str, ref: str, report: Report):
    """
    Compare two directories.
    """

    # scan directories
    src_items = scan_tree(src)
    ref_items = scan_tree(ref)

    # collect items that are in src and ref and will be compared on a content level
    comparable_files = []

    # compare each item
    for relpath, src_item in src_items.items():
        # note extra files
        if relpath not in ref_items:
            report.files_extra.append(relpath)
            continue

        # files are present in src and ref and can be noted for content check
        comparable_files.append(relpath)

    # check for extra files
    for relpath in ref_items:
        # note missing files
        if relpath not in src_items:
            report.files_missing.append(relpath)

    # return report
    return comparable_files
