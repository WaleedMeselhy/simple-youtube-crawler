#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export CRAWL_ROOT=$(pwd)
echo $CRAWL_ROOT
docker-compose down
