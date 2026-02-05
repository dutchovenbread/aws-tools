from __future__ import annotations

import json
from pathlib import Path

from output_parsing import parse_ec2list, parse_gci, parse_rdslist


def test_parse_gci_from_test_data() -> None:
	data_path = (
		Path(__file__).parent
		/ "test_data"
		/ "test_run_AdministratorAccess-070744430225_us-east-1_sts.json"
	)
	with data_path.open("r", encoding="utf-8") as handle:
		response = json.load(handle)

	results = [
		(
			"AdministratorAccess-070744430225",
			"us-east-1",
			"sts",
			response,
		)
	]

	headers, output = parse_gci(results)

	assert headers == ["profile", "region", "userID", "account", "ARN"]
	assert output == [
		[
			"AdministratorAccess-070744430225",
			"us-east-1",
			"AROARA6FSK2I5QBQB5QPY:dutchovenbaker",
			"070744430225",
			"arn:aws:sts::070744430225:assumed-role/AWSReservedSSO_AdministratorAccess_3d985f5dd91498b3/dutchovenbaker",
		]
	]


def test_parse_ec2list_from_test_data_empty() -> None:
	data_path = (
		Path(__file__).parent
		/ "test_data"
		/ "test_run_AdministratorAccess-070744430225_us-east-1_ec2.json"
	)
	with data_path.open("r", encoding="utf-8") as handle:
		response = json.load(handle)

	results = [
		(
			"AdministratorAccess-070744430225",
			"us-east-1",
			"ec2",
			response,
		)
	]

	headers, output = parse_ec2list(results)

	assert headers == ["profile", "region", "instance_id", "status", "instance_type"]
	assert output == []


def test_parse_ec2list_from_test_data_with_results() -> None:
	data_path = (
		Path(__file__).parent
		/ "test_data"
		/ "test_run_AdministratorAccess-357736309526_us-east-2_ec2.json"
	)
	with data_path.open("r", encoding="utf-8") as handle:
		response = json.load(handle)

	results = [
		(
			"AdministratorAccess-357736309526",
			"us-east-2",
			"ec2",
			response,
		)
	]

	headers, output = parse_ec2list(results)

	assert headers == ["profile", "region", "instance_id", "status", "instance_type"]
	assert output == [
		[
			"AdministratorAccess-357736309526",
			"us-east-2",
			"i-0cdc64faa023de43c",
			"running",
			"t3.micro",
		]
	]


def test_parse_rdslist_from_test_data_with_results() -> None:
	data_path = (
		Path(__file__).parent
		/ "test_data"
		/ "test_run_AdministratorAccess-458168469311_us-east-2_rds.json"
	)
	with data_path.open("r", encoding="utf-8") as handle:
		clusters_response = json.load(handle)

	clusters_results = [
		(
			"AdministratorAccess-458168469311",
			"us-east-2",
			"rds",
			clusters_response,
		)
	]
	instances_results: list[tuple[str, str, str, dict]] = []

	headers, output = parse_rdslist(instances_results, clusters_results)

	assert headers == ["profile", "region", "name"]
	assert output == [
		[
			"AdministratorAccess-458168469311",
			"us-east-2",
			"EXERCISEDATABASE",
		]
	]
