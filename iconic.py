#!/usr/bin/env python3
"""Change directory icons easily on MacOS, providing an icon directory."""

import argparse
import glob
import os
import sys

from AppKit import NSImage, NSWorkspace

color = {
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "END": "\033[0m",
    "GREY": "\033[94m",
}


def verify_dir(directory):
    """Verify that a directory exists and is valid"""
    if not os.path.exists(directory):
        print(
            "{}Directory '{}' does not exist!{}".format(
                color["RED"], directory, color["END"]
            )
        )
        return False
    if not os.path.isdir(directory):
        print(
            "{}'{}' is not a directory!{}".format(color["RED"], directory, color["END"])
        )
        return False

    return True


def get_subdirectories(directory, ignore_hidden=False):
    """Return all child directories in a directory"""
    if ignore_hidden:
        return [
            name
            for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name)) and not name.startswith(".")
        ]
    return [
        name
        for name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, name))
    ]


def get_icons(directory):
    """Get all of the icons in a directory"""
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if any(f.endswith(ext) for ext in ["jpg", "ico", "png"])
    ]


def change_icon(folder, icon):
    """Change the icon of a directory"""
    print(
        "{}Changing '{}' to have icon '{}'...{}".format(
            color["CYAN"], folder, icon, color["END"]
        )
    )

    if not NSWorkspace.sharedWorkspace().setIcon_forFile_options_(
        NSImage.alloc().initWithContentsOfFile_(icon), folder, 0
    ):
        print(
            "{}Unable to change folder '{}' to icon '{}'.{}".format(
                color["RED"], folder, icon, color["END"]
            )
        )
        return

    try:
        with open(
            os.path.join(os.path.expanduser("~"), ".cache/iconic/changed"), "a"
        ) as cache_file:
            cache_file.write(folder + "\n")
    except:
        print("{}Unable to write '{}' to cache file.".format(color["RED"], folder))


def process_directory(directory, icons, recursive, ignore_hidden, blacklist):
    index = 0
    subdirectories = get_subdirectories(directory, ignore_hidden)

    for subdirectory in subdirectories:
        target = os.path.join(directory, subdirectory)
        if target not in blacklist:
            change_icon(target, icons[index])
            index = (index + 1) % len(icons)

    if recursive:
        for subdirectory in subdirectories:
            if subdirectory not in blacklist:
                process_directory(
                    os.path.join(directory, subdirectory),
                    icons,
                    recursive,
                    ignore_hidden,
                    blacklist,
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Change directory icons easily on MacOS, providing an icon directory."
    )
    parser.add_argument(
        "-t",
        "--target",
        metavar="target",
        type=str,
        required=True,
        help="Target directory to be changed.",
    )
    parser.add_argument(
        "-s",
        "--source",
        metavar="source",
        type=str,
        required=True,
        help="Source directory of icons.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=False,
        help="Recurse into subdirectories.",
    )
    parser.add_argument(
        "--ignore-hidden",
        action="store_true",
        default=False,
        help="Ignore hidden directories.",
    )
    parser.add_argument(
        "--ignore-cache",
        action="store_true",
        default=False,
        help="Don't blacklist folders from the cache.",
    )
    parser.add_argument("--ignore", action="append", help="Ignore certain directories.")
    args = parser.parse_args()

    if not verify_dir(args.source) or not verify_dir(args.target):
        parser.print_help()
        exit(1)

    cache_dir = os.path.join(os.path.expanduser("~"), ".cache/iconic")
    cache_file = os.path.join(cache_dir, "changed")

    if not os.path.exists(cache_dir):
        os.makedirs(os.path.join(os.path.expanduser("~"), ".cache/iconic"))

    blacklist = []
    if not args.ignore_cache:
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cache:
                for directory in cache:
                    blacklist.append(directory.strip("\n"))

    if args.ignore:
        blacklist += args.ignore

    subdirectories = get_subdirectories(args.target, args.ignore_hidden)
    if len(subdirectories) == 0:
        print(
            "{}No subdirectories located in '{}'!{}".format(
                color["RED"], args.target, color["END"]
            )
        )
        exit(1)

    icons = sorted(get_icons(os.path.abspath(args.source)))
    if len(icons) == 0:
        print(
            "{}No icons located in '{}'!{}".format(
                color["RED"], args.source, color["END"]
            )
        )
        exit(1)

    process_directory(
        os.path.abspath(args.target),
        icons,
        args.recursive,
        args.ignore_hidden,
        blacklist,
    )

    print("{}Operation complete!{}".format(color["GREEN"], color["END"]))
