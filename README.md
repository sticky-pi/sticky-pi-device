# Sticky pi Device

## Directory structure

### `hardware/`

* `BOM.csv`: up-to-date Bill Of Materials (list all the parts, provider, price,...)
* `main.fzz` : Fritzing circuit board for the custom PCB
* `parts/` : 3d parts STL snapshots (and gcodes) from our [Onshape repository](https://cad.onshape.com/documents/73922dc6e3c6d7006b309c14/w/7e4fb88a2e93b6adba33fd5a/e/438cef0dea4f2cfe3bf83d91)


### `software/` 

* `make_image.sh`: a helper script to make an image of the pi os from scratch (emulating a pi on a linux machine -- qemu based)
* `read_onlyfy.sy`: a helper script to make a read-only copy of a os image -- for production
* `burn_image.sh`: wrapper around etcher and fdisk. Use like `burn_image.sh -i <image.img> -d </dev/target-device>`
* `take_picture.py`: the one-shot python service to be run at boot time
* `sync_to_pendrive.py`: one-shot script spawn by `take_picture.py` sends data to pendrive, if detected.
* `os_stub/`: a directory mapping files to be copied to the root of the pi OS
* `dt-blob.dts`: device tree blob containing the mapping of the pi pins (used for camera flash). To be compiled on the host and copied on the image

