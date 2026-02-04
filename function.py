from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Iterable


def invoke_function(
  clients: dict[str, dict[str, dict[str, Any]]],
  function_name: str,
  *,
  parameters: Iterable[Any] | None = None,
) -> list[tuple[str, str, str, Any]]:
  results: list[tuple[str, str, str, Any]] = []
  parameters = list(parameters or [])

  def _call_method(
    profile_name: str,
    region: str,
    client_type: str,
    client: Any,
  ) -> tuple[str, str, str, Any]:
    method = getattr(client, function_name)
    if parameters:
      response = method(*parameters)
    else:
      response = method()
    return profile_name, region, client_type, response

  futures = []
  with ThreadPoolExecutor() as executor:
    for profile_name, regions in clients.items():
      for region, region_clients in regions.items():
        for client_type, client in region_clients.items():
          futures.append(
            executor.submit(_call_method, profile_name, region, client_type, client)
          )

    for future in as_completed(futures):
      results.append(future.result())

  return results
