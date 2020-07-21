#!/bin/bash

ip route add 184.164.236.0/24 via 172.16.0.2 dev eth0
tail -F keep-alive