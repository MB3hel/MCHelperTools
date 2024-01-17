#!/usr/bin/env bash
DIR="$(dirname "$0")"
cd "$DIR"
rm -rf build/
mkdir build/
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -G "Unix Makefiles"
make