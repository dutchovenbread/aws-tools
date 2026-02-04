from __future__ import annotations

from typing import Any, Iterable


def invoke_function(
  clients: dict[str, dict[str, dict[str, Any]]],
  function_name: str,
  invoked_function_parameters: Iterable[Any] | None = None,
) -> list[tuple[str, str, str, Any]]:
  results: list[tuple[str, str, str, Any]] = []
  parameters = list(invoked_function_parameters or [])

  for profile_name, regions in clients.items():
    for region, region_clients in regions.items():
      for client_type, client in region_clients.items():
        method = getattr(client, function_name)
        if parameters:
          response = method(*parameters)
        else:
          response = method()
        results.append((profile_name, region, client_type, response))

  return results
