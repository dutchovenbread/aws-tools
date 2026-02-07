#!/usr/bin/env python3
"""at: AWS tools CLI shell."""

from __future__ import annotations

import argparse
import sys

import yaml

import output_parsing


from clients import create_clients
from function import invoke_function, invoke_function_special_parameters
from key import create_key
from output import write_output


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
  parser.add_argument(
    "-d",
    "--directory",
    default="./cache/",
    metavar="DIR",
    help="Cache directory (default: ./cache/).",
  )
  parser.add_argument(
    "-o",
    "--output",
    default="console",
    choices=["console", "csv", "excel"],
    help="Output format (console, csv, excel).",
  )
  parser.add_argument(
    "-f",
    "--file",
    default="out.csv",
    metavar="FILE",
    help="Output file name (default: out.csv).",
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
  subparsers.add_parser(
    "s3list",
    help="List S3 buckets for all profile/region combinations.",
  )
  subparsers.add_parser(
    "s3sizes",
    help="Get S3 bucket sizing for all profile/region combinations.",
  )
  freeform_parser = subparsers.add_parser(
    "freeform",
    help="Run a freeform command.",
  )
  freeform_parser.add_argument(
    "service",
    help="Service name.",
  )
  freeform_parser.add_argument(
    "freeform_command",
    help="Command name.",
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
  directory = args.directory
  output_format = args.output
  output_file = args.file
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
      directory=directory,
    )
    headers, output = output_parsing.parse_gci(result)
    write_output(headers, output, output_format, output_file)
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
      directory=directory,
    )
    headers, output = output_parsing.parse_ec2list(result)
    write_output(headers, output, output_format, output_file)
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
      directory=directory,
    )
    function_name = "describe_db_clusters"
    clusters_result = invoke_function(
      clients,
      function_name,
      parameters=None,
      read=read,
      write=write,
      key=rerun_token,
      directory=directory,
    )
    headers, output = output_parsing.parse_rdslist(instances_result, clusters_result)
    write_output(headers, output, output_format, output_file)
    return 0

  if args.command == "s3list":
    function_name = "list_buckets"
    sessions, clients = create_clients(profiles, regions, ["s3"])
    result = invoke_function(
      clients,
      function_name,
      parameters=None,
      read=read,
      write=write,
      key=rerun_token,
      directory=directory,
    )
    headers, output = output_parsing.parse_s3list(result)
    write_output(headers, output, output_format, output_file)
    return 0

  if args.command == "s3sizes":
    function_name = "list_buckets"
    sessions, clients = create_clients(profiles, regions, ["s3"])
    result = invoke_function(
      clients,
      function_name,
      parameters=None,
      read=read,
      write=write,
      key=rerun_token,
      directory=directory,
    )
    headers, output = output_parsing.parse_s3list(result)
    bucket_map: dict[str, dict[str, list[str]]] = {}
    for profile_name, region, bucket_name in output:
      bucket_map.setdefault(profile_name, {}).setdefault(region, []).append(bucket_name)
    sessions, cloudwatch_clients = create_clients(profiles, regions, ["cloudwatch"])
    cloudwatch_parameters = {}
    for key_profile, regions in bucket_map.items():
      for key_region, buckets in regions.items():
        for bucket in buckets:
          cloudwatch_parameters.setdefault(key_profile, {}).setdefault(key_region, {})[bucket] = {
            "Namespace": "AWS/S3",
            "MetricName": "BucketSizeBytes",
            "Dimensions": [
              {"Name": "BucketName", "Value": bucket},
              {"Name": "StorageType", "Value": "StandardStorage"},
            ],
            "StartTime": "2024-01-01T00:00:00Z",
            "EndTime": "2024-12-31T23:59:59Z",
            "Period": 86400,
            "Statistics": ["Average"],
          }
    cloudwatch_results = invoke_function_special_parameters(
      cloudwatch_clients,
      "get_metric_statistics",
      parameters_dict=cloudwatch_parameters,
      read=read,
      write=write,
      key=rerun_token,
      directory=directory,
    )

    headers, output = output_parsing.parse_s3sizes(cloudwatch_results)
    write_output(headers, output, output_format, output_file)

    return 0

  if args.command == "freeform":
    print(f'Running freeform command: {args.service} {args.freeform_command}')
    if not args.service or not args.freeform_command:
      parser.error("freeform requires two arguments: service and command")
    sessions, clients = create_clients(profiles, regions, [args.service])
    result = invoke_function(
      clients,
      args.freeform_command,
      parameters=None,
      read=read,
      write=write,
      key=rerun_token,
      directory=directory,
    )
    for profile_name, region, client_type, response in result:
      print(f"{profile_name} {region} {client_type}")
      if isinstance(response, dict):
        for key, value in response.items():
          print(f"{key}: {value}")
      else:
        print(response)
    return 0


  # TODO: route subcommands here

  return 0


if __name__ == "__main__":
  raise SystemExit(main(sys.argv[1:]))
