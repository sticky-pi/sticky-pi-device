# Sticky Pi Software

We make a local image from the stock Archlinux operating system, 
then we transfer custom files on it before we use QEMU to spawn a virtual machine on this image. Once in the virtual machine, 
we install dependencies and continue the configuration of the virtual image. In the end. We compress the resulting image 
(YYYY-MM-dd_sticky_pi_rpi.img.gz) --that can be burnt and used directly. The whole process is orchestrated by a Makefile 

* `src` -- a small python package, `sticky_pi_device`, that will be installed on the Raspberry Pi
* `take_picture` -- a C program to take the picture (adapted from [raspistill](https://github.com/raspberrypi/userland/blob/master/host_applications/linux/apps/raspicam/))
* `.env` -- definition of environment variables used at build and runtime (e.g. directory location, camera setting, ...)
* `Makefile` -- A tool to build the full image of a Sticky Pi. Needs to be run as superuser under a linux system **at your own risks**.
* `os_stub/` -- a directory mapping files to be copied to the root of the pi OS
* `utils` -- a set of scripts used during the image building process
* `prototypes/` -- a directory for developers to, for instance, create mock devices 


To build the image:
```sh
sudo make all
```
