#!/bin/bash
# BAUMER_GAPI=baumer/baumer-gapi-sdk-linux-v2.10.0.25119-gcc-5.4-aarch64.tar.gz
BAUMER_GAPI=baumer/baumer-gapi-sdk-linux-v2.10.1-gcc-5.4-aarch64.tar.gz
BAUMER_EXTR=baumer

rm -r $BAUMER_EXTR/doc
rm -r $BAUMER_EXTR/examples
rm -r $BAUMER_EXTR/include
rm -r $BAUMER_EXTR/lib
rm -r $BAUMER_EXTR/tools
rm -r $BAUMER_EXTR/udev

tar xf $BAUMER_GAPI -C $BAUMER_EXTR
