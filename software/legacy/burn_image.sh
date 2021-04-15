#!/usr/bin/env bash

while getopts ":i:d:" o; do
    case "${o}" in
        i)
            OS_IMG_NAME=$OPTARG
            ;;
        d)
            SD=$OPTARG
            ;;
        *)
            usage
            ;;
    esac
done
echo "burning ${OS_IMG_NAME} on ${SD}"
set -e
etcher-cli  $OS_IMG_NAME -u false -d $SD
set +e
fdisk $SD << EOF
n
p
3


t
3
c
w
EOF
set -e
echo "fdisk non-zero exit status"
# make fat32 file system on the new partition
partprobe $SD
mkfs.vfat ${SD}p3
echo labeling ${SD}p3 as ${SPI_DRIVE_LABEL}
fatlabel  ${SD}p3 ${SPI_DRIVE_LABEL}