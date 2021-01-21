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
    dirname = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
    data_path = os.path.join(DATA_PATH, exp, dirname)
    exists = os.path.exists(data_path)

    os.makedirs(data_path)

    # Run experiment
    run = experiments[exp]
    run(args, data_path)
