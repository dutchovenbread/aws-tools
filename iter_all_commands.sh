#!/usr/bin/env bash
set -euo pipefail

subcommands=(
	debug
	gci
	ec2list
	rdslist
	s3list
	s3sizes
	example
)

for subcommand in "${subcommands[@]}"; do
	at -t iter_run --write "$subcommand"
done
