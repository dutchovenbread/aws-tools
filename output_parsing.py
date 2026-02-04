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
