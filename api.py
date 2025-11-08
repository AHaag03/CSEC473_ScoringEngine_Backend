from flask import Flask, jsonify
from config import load_config
import sqlite_storage

app = Flask(__name__)

@app.route("/scores", methods=["GET"])
def get_scores():
    cfg = load_config()
    team_ids = cfg["team_ids"]
    team_names = cfg["team_names"]
    base_hosts = cfg["base_hosts"]

    db_scores = sqlite_storage.read_all_scores()
    latest_status = sqlite_storage.read_latest_status_by_host_and_service()

    teams_output = []
    for tid in team_ids:
        tname = team_names.get(tid, f"Team {tid}")
        team_score_total = 0
        team_hosts_output = []

        for bh in base_hosts:
            if not bh.in_scope:
                continue

            expanded_name = f"{bh.name}-t{tid}"
            host_score = db_scores.get(expanded_name, 0)
            team_score_total += host_score

            services_output = []
            for svc in bh.services:
                svc_up = latest_status.get((expanded_name, svc), False)
                services_output.append({"name": svc, "up": svc_up})

            team_hosts_output.append({
                "name": bh.name,
                "services": services_output
            })

        teams_output.append({
            "name": tname,
            "icon": "",
            "score": team_score_total,
            "hosts": team_hosts_output
        })

    return jsonify({"teams": teams_output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
