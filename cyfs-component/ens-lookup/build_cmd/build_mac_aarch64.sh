#!/bin/sh
cd ../src
go build -o ../bin/aarch64/ -ldflags "-s -w"