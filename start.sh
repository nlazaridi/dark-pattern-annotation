#!/bin/bash
set -e
apt-get update && apt-get install -y git-lfs
git lfs install
git lfs pull
python annotation_server.py 