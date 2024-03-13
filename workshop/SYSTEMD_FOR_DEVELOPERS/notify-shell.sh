#!/usr/bin/env bash


bash -c 'systemd-notify --ready --status="Waiting for data…"'

exec sleep 5