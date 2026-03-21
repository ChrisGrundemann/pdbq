#!/bin/sh
set -e

# Fix ownership of the Fly.io volume mount, which is owned by root at first boot.
# This runs as root before dropping to appuser.
chown -R appuser:appuser /app/data

exec gosu appuser "$@"
