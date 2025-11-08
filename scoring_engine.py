from datetime import datetime
from config import load_config
from service_checks import SERVICE_REGISTRY
import sqlite_storage

POINTS_PER_SERVICE = 5

class ScoringEngine:
    def __init__(self):
        cfg = load_config()
        self.poll_interval = cfg["poll_interval"]
        self.expanded_hosts = cfg["expanded_hosts"]
        self.service_ports = cfg["service_ports"]
        sqlite_storage.init_db()
        self.scores = sqlite_storage.read_all_scores()

    def run_once(self):
        tcp = SERVICE_REGISTRY["tcp"]

        for host in self.expanded_hosts:
            for svc in host.services:
                port = self.service_ports.get(svc)
                if port is None:
                    continue

                ok, msg = tcp(host.ip, int(port))
                pts = POINTS_PER_SERVICE if ok else 0

                sqlite_storage.save_check(host.name, host.ip, svc, ok, pts, msg)
                if ok:
                    sqlite_storage.upsert_score(host.name, pts)

                print(f"[{datetime.utcnow().isoformat()}] {host.name} {svc} ({host.ip}:{port}) → {msg}")

    def print_hosts(self):
        for host in self.expanded_hosts:
            print(host)

    def get_scores(self):
        return dict(self.scores)
