#!/bin/bash

if (($# < 1)); then
    echo "Usage: ./stop.sh node"
    exit
fi

wg-quick down wg0-$1
