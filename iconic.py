#!/usr/bin/env python
"""Change directory icons easily on MacOS, providing an icon directory."""

import argparse
import Cocoa
import sys
import glob
import os

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


def get_subdirectories(directory):
    """Return all child directories in a directory"""
    return [
        name
        for name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, name))
    ]


def get_icons(directory):
    """Get all of the icons in a directory"""
    return [
        directory + f
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
    try:
        Cocoa.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(
            Cocoa.NSImage.alloc().initWithContentsOfFile_(icon), folder, 0
        )
    except:
        print(
            "{}Unable to change folder '{}' to icon '{}'.{}".format(
                color["RED"], folder, icon, color["END"]
            )
        )


def process_directory(directory, icons, recursive):
    index = 0
    subdirectories = get_subdirectories(directory)
    for subdirectory in subdirectories:
        target = os.path.join(directory, subdirectory)
        change_icon(target, icons[index])
        index = (index + 1) % len(icons)
        if recursive:
            process_directory(os.path.join(directory, subdirectory), icons, recursive)


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
    args = parser.parse_args()

    if not verify_dir(args.source) or not verify_dir(args.target):
        parser.print_help()
        exit(1)

    subdirectories = get_subdirectories(args.target)
    if len(subdirectories) == 0:
        print(
            "{}No subdirectories located in '{}'!{}".format(
                color["RED"], args.target, color["END"]
            )
        )
        exit(1)

    icons = sorted(get_icons(args.source))
    if len(icons) == 0:
        print(
            "{}No icons located in '{}'!{}".format(
                color["RED"], args.source, color["END"]
            )
        )
        exit(1)

    process_directory(args.target, icons, args.recursive)

    print("{}Operation complete!{}".format(color["GREEN"], color["END"]))
