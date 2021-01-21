#!/usr/bin/env python3
import argparse
import os
import datetime

from src.latency import RunLatencyCustomers

DATA_PATH = "data"

experiments = {
    'latency-optin': RunLatencyCustomers
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment', choices=experiments.keys())
    parser.add_argument('--src')
    parser.add_argument('--dst')
    args = parser.parse_args()

    exp = args.experiment

    # Prepare output directory
    exp_root = os.path.join(DATA_PATH, exp)
    if not os.path.exists(exp_root):
        os.mkdir(exp_root)

    today = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
    i = 0
    data_path = ""
    exists = True
    while exists:
        dirname = f"{today}_{i}"
        data_path = os.path.join(exp_root, dirname)
        exists = os.path.exists(data_path)

    os.mkdir(data_path)

    # Run experiment
    run = experiments[exp]
    run(args, data_path)
