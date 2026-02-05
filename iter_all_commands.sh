#!/usr/bin/env bash
set -euo pipefail

subcommands=(
	debug
	gci
	ec2list
	rdslist
	example
)

for subcommand in "${subcommands[@]}"; do
	at -t test_run --write "$subcommand"
done
