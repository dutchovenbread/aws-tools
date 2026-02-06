from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def build_filename(
  profile_name: str,
  region: str,
  client_type: str,
  key: str | None,
  directory: str,
) -> Path:
  cache_dir = Path(directory)
  cache_dir.mkdir(parents=True, exist_ok=True)
  key_prefix = f"{key}_" if key else ""
  return cache_dir / f"{key_prefix}{profile_name}_{region}_{client_type}.json"


def build_filename_with_nickname(
  profile_name: str,
  region: str,
  client_type: str,
  nickname: str,
  key: str | None,
  directory: str,
) -> Path:
  cache_dir = Path(directory)
  cache_dir.mkdir(parents=True, exist_ok=True)
  key_prefix = f"{key}_" if key else ""
  return cache_dir / f"{key_prefix}{profile_name}_{region}_{client_type}_{nickname}.json"


def invoke_function(
  clients: dict[str, dict[str, dict[str, Any]]],
  function_name: str,
  *,
  parameters: Iterable[Any] | None = None,
  read: bool = False,
  write: bool = False,
  key: str | None = None,
  directory: str = "./cache/",
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
    directory: str,
  ) -> tuple[str, str, str, Any]:
    cache_path = build_filename(profile_name, region, client_type, key, directory)
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
              directory,
            )
          )

    for future in as_completed(futures):
      results.append(future.result())

  return results


def invoke_function_special_parameters(
  clients: dict[str, dict[str, dict[str, Any]]],
  function_name: str,
  parameters_dict: Mapping[str, Mapping[str, Mapping[str, Any]]],
  *,
  read: bool = False,
  write: bool = False,
  key: str | None = None,
  directory: str = "./cache/",
) -> list[tuple[str, str, str, str, Any]]:
  results: list[tuple[str, str, str, str, Any]] = []

  def _call_method_for_region(
    profile_name: str,
    region: str,
    region_clients: dict[str, Any],
    region_parameters: Mapping[str, Any],
    read: bool,
    write: bool,
    key: str | None,
    directory: str,
  ) -> list[tuple[str, str, str, str, Any]]:
    local_results: list[tuple[str, str, str, str, Any]] = []
    for client_type, client in region_clients.items():
      method = getattr(client, function_name)
      for nickname, params in region_parameters.items():
        cache_path = build_filename_with_nickname(
          profile_name,
          region,
          client_type,
          nickname,
          key,
          directory,
        )
        if read and cache_path.exists():
          with cache_path.open("r", encoding="utf-8") as handle:
            response = json.load(handle)
        else:
          if params is None:
            response = method()
          elif isinstance(params, dict):
            response = method(**params)
          else:
            response = method(*params)
          if write:
            with cache_path.open("w", encoding="utf-8") as handle:
              json.dump(response, handle, default=str)
        local_results.append((profile_name, region, client_type, nickname, response))
    return local_results

  futures = []
  with ThreadPoolExecutor() as executor:
    for profile_name, regions in clients.items():
      profile_params = parameters_dict.get(profile_name, {})
      for region, region_clients in regions.items():
        region_parameters = profile_params.get(region, {})
        futures.append(
          executor.submit(
            _call_method_for_region,
            profile_name,
            region,
            region_clients,
            region_parameters,
            read,
            write,
            key,
            directory,
          )
        )

    for future in as_completed(futures):
      results.extend(future.result())

  return results
