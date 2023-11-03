#!/bin/sh
cd ../src
env GOOS=darwin GOARCH=amd64 CC=musl-cross-x86_64-apple-darwin go build -o ../bin/x86_64/ -ldflags "-s -w"