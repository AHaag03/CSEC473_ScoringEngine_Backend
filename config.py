import os, json
from dotenv import load_dotenv
from typing import List, Dict, Any
from models import BaseHost, ExpandedHost

load_dotenv()

def _clean_json_string(raw: str) -> str:
    if not raw:
        return raw
    raw = raw.strip()
    if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        return raw[1:-1]
    return raw

def _load_json_env(key: str, default: str):
    raw = os.getenv(key, default)
    raw = _clean_json_string(raw)
    return json.loads(raw)

def load_config() -> Dict[str, Any]:
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    team_ids = _load_json_env("TEAM_IDS", "[1,2,3]")
    team_names_raw = _load_json_env("TEAM_NAMES_JSON", "{}")
    team_names = {int(k): v for k, v in team_names_raw.items()}
    service_ports = _load_json_env("SERVICES_JSON", "{}")
    hosts_data = _load_json_env("HOSTS_JSON", "[]")

    base_hosts = [
        BaseHost(
            name=h["name"],
            ip_template=h["ip"],
            in_scope=bool(h.get("in_scope", False)),
            services=h.get("services", [])
        )
        for h in hosts_data
    ]

    expanded_hosts: List[ExpandedHost] = []
    for bh in base_hosts:
        if not bh.in_scope:
            continue
        if "X" in bh.ip_template:
            for tid in team_ids:
                expanded_hosts.append(
                    ExpandedHost(
                        name=f"{bh.name}-t{tid}",
                        base_name=bh.name,
                        ip=bh.ip_template.replace("X", str(tid)),
                        team_id=tid,
                        services=bh.services
                    )
                )
        else:
            for tid in team_ids:
                expanded_hosts.append(
                    ExpandedHost(
                        name=f"{bh.name}-t{tid}",
                        base_name=bh.name,
                        ip=bh.ip_template,
                        team_id=tid,
                        services=bh.services
                    )
                )

    return {
        "poll_interval": poll_interval,
        "team_ids": team_ids,
        "team_names": team_names,
        "base_hosts": base_hosts,
        "expanded_hosts": expanded_hosts,
        "service_ports": service_ports,
    }
