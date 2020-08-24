#!/bin/bash

if (($# < 1)); then
    echo "Usage: ./start.sh node"
    exit
fi

wg-quick up wg0-$1
