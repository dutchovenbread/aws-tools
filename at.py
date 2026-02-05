#!/usr/bin/env python3
"""at: AWS tools CLI shell."""

from __future__ import annotations

import argparse
import sys

import yaml

import output_parsing


from clients import create_clients
from function import invoke_function
from key import create_key
from output import console_print


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
  parser.add_argument(
    "-t",
    "--reruntoken",
    metavar="TOKEN",
    help="Rerun token to rerun against data from a previous run.",
  )
  parser.add_argument(
    "--read",
    action="store_true",
    help="Enable read mode.",
  )
  parser.add_argument(
    "--write",
    action="store_true",
    help="Enable write mode.",
  )

  subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
  subparsers.required = False

  subparsers.add_parser("debug", help="Print debug information.")
  subparsers.add_parser(
    "gci",
    help="Get caller identity for all profile/region combinations.",
  )
  subparsers.add_parser(
    "ec2list",
    help="List EC2 instances for all profile/region combinations.",
  )
  subparsers.add_parser(
    "rdslist",
    help="List RDS instances for all profile/region combinations.",
  )
  # Placeholder subcommand
  subparsers.add_parser("example", help="Example subcommand (placeholder).")

  return parser


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)
  config = args.config
  profile = args.profile
  rerun_token = args.reruntoken
  read = args.read
  write = args.write
  if write and not rerun_token:
    rerun_token = create_key()
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
    print("at 0.2.0")
    return 0

  if args.command is None:
    parser.print_help()
    return 0

  if args.command == "debug":
    print(f'config file: {config}')
    print(f'profiles: {profiles}')
    print(f'regions: {regions}')
    return 0

  if args.command == "gci":
    function_name = "get_caller_identity"
    sessions, clients = create_clients(profiles, regions, ["sts"])
    result = invoke_function(
      clients,
      function_name,
      parameters=None,
      read=read,
      write=write,
      key=rerun_token,
    )
    headers, output = output_parsing.parse_gci(result)
    console_print(headers, output)
    return 0

  if args.command == "ec2list":
    function_name = "describe_instances"
    sessions, clients = create_clients(profiles, regions, ["ec2"])
    result = invoke_function(
      clients,
      function_name,
      parameters=None,
      read=read,
      write=write,
      key=rerun_token,
    )
    headers, output = output_parsing.parse_ec2list(result)
    console_print(headers, output)
    return 0

  if args.command == "rdslist":
    function_name = "describe_db_instances"
    sessions, clients = create_clients(profiles, regions, ["rds"])
    instances_result = invoke_function(
      clients,
      function_name,
      parameters=None,
      read=read,
      write=write,
      key=rerun_token,
    )
    function_name = "describe_db_clusters"
    clusters_result = invoke_function(
      clients,
      function_name,
      parameters=None,
      read=read,
      write=write,
      key=rerun_token,
    )
    headers, output = output_parsing.parse_rdslist(instances_result, clusters_result)
    console_print(headers, output)
    return 0

  # TODO: route subcommands here

  return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv[1:]))
