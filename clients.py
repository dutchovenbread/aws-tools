from __future__ import annotations

from typing import Iterable

import boto3


def create_clients(
  profiles: Iterable[str],
  regions: Iterable[str],
  client_types: Iterable[str],
) -> tuple[dict[str, dict[str, boto3.session.Session]], dict[str, dict[str, dict[str, object]]]]:
  sessions: dict[str, dict[str, boto3.session.Session]] = {}
  clients: dict[str, dict[str, dict[str, object]]] = {}

  for profile_name in profiles:
    sessions[profile_name] = {}
    clients[profile_name] = {}
    for region in regions:
      session = boto3.Session(profile_name=profile_name, region_name=region)
      sessions[profile_name][region] = session
      clients[profile_name][region] = {}
      for client_type in client_types:
        clients[profile_name][region][client_type] = session.client(client_type)

  return sessions, clients
