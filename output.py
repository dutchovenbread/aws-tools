from __future__ import annotations


def console_print(headers: list[str], output: list[list[str]]) -> None:
	print(",".join(headers))
	for row in output:
		template = "{}," * (len(row) - 1) + "{}"
		print(template.format(*row))