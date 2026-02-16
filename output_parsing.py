from __future__ import annotations

from typing import Any


def parse_gci(
	results: list[tuple[str, str, str, dict[str, Any]]],
) -> tuple[list[str], list[list[str]]]:
	headers = ["profile", "region", "userID", "account", "ARN"]
	output: list[list[str]] = []

	for profile, region, _client_type, response in results:
		output.append(
			[
				profile,
				region,
				str(response.get("UserId", "")),
				str(response.get("Account", "")),
				str(response.get("Arn", "")),
			]
		)

	return headers, output


def parse_ec2list(
	results: list[tuple[str, str, str, dict[str, Any]]],
) -> tuple[list[str], list[list[str]]]:
	headers = ["profile", "region", "instance_id", "status", "instance_type"]
	output: list[list[str]] = []

	for profile, region, _client_type, response in results:
		for reservation in response.get("Reservations", []) or []:
			for instance in reservation.get("Instances", []) or []:
				output.append(
					[
						profile,
						region,
						str(instance.get("InstanceId", "")),
						str(instance.get("State", {}).get("Name", "")),
						str(instance.get("InstanceType", "")),
					]
				)

	return headers, output


def parse_ebslist(
	results: list[tuple[str, str, str, dict[str, Any]]],
) -> tuple[list[str], list[list[str]]]:
	headers = ["profile", "region", "volume_id", "state", "size", "volume_type", "iops"]
	output: list[list[str]] = []

	for profile, region, _client_type, response in results:
		for volume in response.get("Volumes", []) or []:
			output.append(
				[
					profile,
					region,
					str(volume.get("VolumeId", "")),
					str(volume.get("State", "")),
					str(volume.get("Size", "")),
					str(volume.get("VolumeType", "")),
					str(volume.get("Iops", "")),
				]
			)

	return headers, output


def parse_rdslist(
	instances: list[tuple[str, str, str, dict[str, Any]]],
	clusters: list[tuple[str, str, str, dict[str, Any]]],
) -> tuple[list[str], list[list[str]]]:
	headers = ["profile", "region", "name"]
	output: list[list[str]] = []

	for profile, region, _client_type, response in clusters:
		for cluster in response.get("DBClusters", []) or []:
			output.append(
				[
					profile,
					region,
					str(cluster.get("DatabaseName", "")),
				]
			)
	for profile, region, _client_type, response in instances:
		for instance in response.get("DBInstances", []) or []:
			output.append(
				[
					profile,
					region,
					str(instance.get("DBName", "")),
				]
			)

	return headers, output


def parse_s3list(
	results: list[tuple[str, str, str, dict[str, Any]]],
) -> tuple[list[str], list[list[str]]]:
	headers = ["profile", "region", "bucket_name"]
	output: list[list[str]] = []

	for profile, region, _client_type, response in results:
		for bucket in response.get("Buckets", []) or []:
			output.append(
				[
					profile,
					region,
					str(bucket.get("Name", "")),
				]
			)

	return headers, output


def parse_s3sizes(
	results: list[tuple[str, str, str, dict[str, Any]]],
) -> tuple[list[str], list[list[str]]]:
	
  headers = ["profile", "region", "bucket_name", "size in MB"]
  output: list[list[str]] = []
	
  for profile, region, _client_type, bucket_name, response in results:
    if response['Datapoints']:
      # Get the most recent data point
      latest_datapoint = sorted(response['Datapoints'], key=lambda x: x['Timestamp'], reverse=True)[0]
      size_bytes = int(latest_datapoint['Average'])
      size_mb = size_bytes / (1024 ** 2)
    else:
      size_mb = None


    output.append([
      profile,
      region,
      bucket_name,
      size_mb,
    ])
  return headers, output