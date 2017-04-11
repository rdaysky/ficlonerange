#!/usr/bin/python3

import sys
import os
from fcntl import ioctl
import struct
import argparse
import errno
import textwrap

def fail(message):
    print(textwrap.fill("FICLONERANGE: " + message))
    sys.exit(3)

FICLONERANGE = 0x4020940d

def struct_file_clone_range(src_fd, src_offset, src_length, dst_offset):
    return struct.pack("qQQQ", src_fd, src_offset, src_length, dst_offset)

parser = argparse.ArgumentParser(description="Reflink bytes from source file to destination. "
    "If no optional parameters are provided, append contents of src to dest. See ioctl_ficlonerange(2) for details.")
parser.add_argument("-s", type=int, default=0, help="Source file offset in bytes (default: 0)")
parser.add_argument("-l", type=int, default=0, help="Number of bytes to reflink (default: all data)")
parser.add_argument("-d", type=int,            help="Destination file offset in bytes (default: end of file)")
parser.add_argument("src", help="Source filename")
parser.add_argument("dest", help="Destination filename")
args = parser.parse_args()

src_fd = os.open(args.src, os.O_RDONLY)
dst_fd = os.open(args.dest, os.O_WRONLY)

try:
    ioctl(dst_fd, FICLONERANGE, struct_file_clone_range(src_fd,
        args.s or 0,
        args.l or 0,
        args.d if args.d is not None else os.fstat(dst_fd).st_size,
    ))
except OSError as e:
    if e.errno == errno.EXDEV:
        fail("src and dest are not on the same mounted filesystem")

    if e.errno == errno.EISDIR:
        fail("One of the files is a directory and the filesystem does not support shared regions in directories.")

    if e.errno == errno.EINVAL:
        fail("The filesystem does not support reflinking the ranges of the given files. This error can also appear "
            "if either file descriptor represents a device, FIFO, or socket. Disk filesystems generally require the "
            "offset and length arguments to be aligned to the fundamental block size ({} bytes). XFS and Btrfs do not support "
            "overlapping reflink ranges in the same file.".format(os.fstat(dst_fd).st_blksize))

    if e.errno == errno.EBADF:
        fail("Filesystem does not support reflink (EBADF).")

    if e.errno == errno.EPERM:
        fail("dest is immutable.")

    if e.errno == errno.ETXTBSY:
        fail("One of the files is a swap file. Swap files cannot share storage.")

    if e.errno == errno.EOPNOTSUPP:
        fail("Filesystem does not support reflink (EOPNOTSUPP).")

    raise
