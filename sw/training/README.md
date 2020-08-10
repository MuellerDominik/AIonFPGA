# Training

The [dataset](https://drive.switch.ch/index.php/s/wuTr9A3i5q3HSbd) (individual frames) must be located at `./AIonFPGA/sw/training/build/dataset/frames`.

This can be done by using the following commands:

```bash
$ curl -o fhnw_toys.tar.gz https://drive.switch.ch/index.php/s/wuTr9A3i5q3HSbd/download
$ mkdir -p ./AIonFPGA/sw/training/build/dataset/frames
$ tar -xzvf fhnw_toys.tar.gz --strip-components=2 -C ./AIonFPGA/sw/training/build/dataset/frames
```

The SHA-256 checksum of the `fhnw_toys.tar.gz` can be calculated with the following command:

```bash
$ sha256sum fhnw_toys.tar.gz
59b25292414ede0f2809d3262c16eeaad30935ce7ec0c737cc54bad41d80311f  fhnw_toys.tar.gz
```
