# Camera (libcamera.so)

To avoid image acquisition issues on Linux, the USB-FS buffer memory limit can be increased to 1000 MB from the default 16 MB. This can prevent crashes associated with buffer allocation when starting the camera.

```
echo 500 | sudo tee /sys/module/usbcore/parameters/usbfs_memory_mb
```
