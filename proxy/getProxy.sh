#!/bin/sh

# Remove proxy.zip if exists
[ -e proxy ] && rm proxy

# Download proxy.zip
if [ "$(uname)" == "Darwin" ]; then
    curl -sSL https://github.com/improbable-eng/grpc-web/releases/download/v0.14.0/grpcwebproxy-v0.14.0-osx-x86_64.zip > proxy.zip
elif [ "$(uname)" == "Linux" ]; then
    curl -sSL https://github.com/improbable-eng/grpc-web/releases/download/v0.14.0/grpcwebproxy-v0.14.0-linux-x86_64.zip > proxy.zip
fi

# Unzip
unzip proxy.zip

# Move and rename
mv dist/grpcwebproxy* proxy

# Remove temp files
rm proxy.zip
rm -r dist