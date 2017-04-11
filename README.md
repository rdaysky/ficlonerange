Ever wondered why `cp --reflink` exists and `cat --reflink` doesn’t? Now you can merge and split files avoiding both time and space costs using this simple Python script that just performs the FICLONERANGE ioctl. Note it only works on some filesystems (I only tested it on btrfs) and is subject to alignment constraints (only works on chunks that are multiples of block size, typically 4k).

Possible use cases include joining VOB files from DVDs, or other large files that for some reason come in chunks.

For usage, pass the script the `--help` argument.
