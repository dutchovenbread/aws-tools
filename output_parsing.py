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


def parse_rdslist(
	results: list[tuple[str, str, str, dict[str, Any]]],
) -> tuple[list[str], list[list[str]]]:
	headers = ["profile", "region", "name"]
	output: list[list[str]] = []

	for profile, region, _client_type, response in results:
		for cluster in response.get("DBClusters", []) or []:
			output.append(
				[
					profile,
					region,
					str(cluster.get("DatabaseName", "")),
				]
			)
		for instance in response.get("DBInstances", []) or []:
			output.append(
				[
					profile,
					region,
					str(instance.get("DBName", "")),
				]
			)

	return headers, output
