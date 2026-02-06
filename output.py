from __future__ import annotations

import csv

from openpyxl import Workbook


def write_output(
	headers: list[str],
	output: list[list[str]],
	out_type: str,
	filename: str,
) -> None:
	print(",".join(headers))
	for row in output:
		template = "{}," * (len(row) - 1) + "{}"
		print(template.format(*row))

	if out_type == "csv":
		with open(filename, "w", newline="", encoding="utf-8") as handle:
			writer = csv.writer(handle)
			writer.writerow(headers)
			writer.writerows(output)

	if out_type == "excel":
		workbook = Workbook()
		worksheet = workbook.active
		worksheet.append(headers)
		for row in output:
			worksheet.append(row)
		workbook.save(filename)