#!/usr/bin/env python3
"""at: AWS tools CLI shell."""

from __future__ import annotations

import argparse
import sys

import yaml


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="at",
    description="AWS tools command-line interface.",
  )
  parser.add_argument(
    "-v",
    "--version",
    action="store_true",
    help="Show version and exit.",
  )
  parser.add_argument(
    "-c",
    "--config",
    default="config.yaml",
    metavar="FILE",
    help="Path to config file (default: config.yaml).",
  )
  parser.add_argument(
    "-p",
    "--profile",
    metavar="PROFILE",
    help="AWS profile name to use.",
  )
  parser.add_argument(
    "-r",
    "--region",
    default=None,
    metavar="REGION",
    help="AWS region to use.",
  )

  subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
  subparsers.required = False

  subparsers.add_parser("debug", help="Print debug information.")
  # Placeholder subcommand
  subparsers.add_parser("example", help="Example subcommand (placeholder).")

  return parser


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)
  config = args.config
  profile = args.profile
  with open(config, "r", encoding="utf-8") as handle:
    config_data = yaml.safe_load(handle) or {}
  if profile:
    profiles = [profile]
  else:
    profiles = config_data.get("profiles", [])
  if args.region:
    regions = [args.region]
  else:
    regions = config_data.get("regions", ["us-east-2"])

  if args.version:
    print("at 0.1.0")
    return 0

  if args.command is None:
    parser.print_help()
    return 0

  if args.command == "debug":
    print(f'config file: {config}')
    print(f'profiles: {profiles}')
    print(f'regions: {regions}')
    return 0

  # TODO: route subcommands here

  return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv[1:]))
