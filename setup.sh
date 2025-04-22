#!/usr/bin/env bash
# Create or update and activate vosk_env
conda env create -f environment.yml --force || conda env update -f environment.yml --prune
conda activate vosk_env
