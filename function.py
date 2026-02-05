from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
from typing import Any, Iterable


def build_filename(
  profile_name: str,
  region: str,
  client_type: str,
  key: str | None,
) -> Path:
  cache_dir = Path("cache")
  cache_dir.mkdir(parents=True, exist_ok=True)
  key_prefix = f"{key}_" if key else ""
  return cache_dir / f"{key_prefix}{profile_name}_{region}_{client_type}.json"


def invoke_function(
  clients: dict[str, dict[str, dict[str, Any]]],
  function_name: str,
  *,
  parameters: Iterable[Any] | None = None,
  read: bool = False,
  write: bool = False,
  key: str | None = None,
) -> list[tuple[str, str, str, Any]]:
  results: list[tuple[str, str, str, Any]] = []
  parameters = list(parameters or [])

  def _call_method(
    profile_name: str,
    region: str,
    client_type: str,
    client: Any,
    read: bool,
    write: bool,
    key: str | None,
  ) -> tuple[str, str, str, Any]:
    cache_path = build_filename(profile_name, region, client_type, key)
    if read and cache_path.exists():
      with cache_path.open("r", encoding="utf-8") as handle:
        response = json.load(handle)
    else:
      method = getattr(client, function_name)
      if parameters:
        response = method(*parameters)
      else:
        response = method()
      if write:
        with cache_path.open("w", encoding="utf-8") as handle:
          json.dump(response, handle, default=str)
    return profile_name, region, client_type, response

  futures = []
  with ThreadPoolExecutor() as executor:
    for profile_name, regions in clients.items():
      for region, region_clients in regions.items():
        for client_type, client in region_clients.items():
          futures.append(
            executor.submit(
              _call_method,
              profile_name,
              region,
              client_type,
              client,
              read,
              write,
              key,
            )
          )

    for future in as_completed(futures):
      results.append(future.result())

  return results
