# Hardware  and Software for the [Sticky Pi] devices(https://sticky-pi.github.io)

**This readme is intended for contributors and developers**. 
Instructions to assemble Sticky Pis are available on [our documentation](https://doc.sticky-pi.com/hardware.html)

----------------------------- 

## Directory structure

### `hardware/`

* `BOM.csv` -- up-to-date Bill Of Materials (list all the parts, provider, price,...)
* `main.fzz` -- Fritzing circuit board for the custom PCB
* `parts/` -- 3d parts STL snapshots (and gcodes) from our [Onshape repository](https://cad.onshape.com/documents/73922dc6e3c6d7006b309c14/w/7e4fb88a2e93b6adba33fd5a/e/438cef0dea4f2cfe3bf83d91)


### `software/` 
Contains files and tools to build the Sticky Pi OS. Briefly, we make a local image from the stock Archlinux operating system, 
then we transfer custom files on it before we use QEMU to spawn a virtual machine on this image. Once in the virtual machine, 
we install dependencies and continue the configuration of the virtual image. In the end. We compress the resulting image 
(YYYY-MM-dd_sticky_pi_rpi.img.gz) --that can be burnt and used directly. The whole process is orchestrated by a Makefile 

* `src` -- a small python package, `sticky_pi_device`, that will be installed on the Raspberry Pi
* `.env` -- definition of environment variables used at build and runtime (e.g. directory location, camera setting, ...)
* `Makefile` -- A tool to build the full image of a Sticky Pi. Needs to be run as super user under a linux system **at your own risks**.
* `os_stub/` -- a directory mapping files to be copied to the root of the pi OS
* `utils` -- a set of scripts used during the image building process


To build the image:
```sh
sudo make all
```

