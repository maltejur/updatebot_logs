#!/usr/bin/env python3

import os
import requests
from thclient import TreeherderClient
from datetime import datetime, timedelta

client = TreeherderClient()

if not os.path.isdir("logs"):
    os.mkdir("logs")

expired_date = datetime.now() - timedelta(days=89)

jobs = client.get_jobs(
    "mozilla-central", job_type_name="updatebot-cron", count=None, submit_time__gt=expired_date.isoformat()
)
for i, job in enumerate(jobs):
    print(f"\r{i + 1} / {len(jobs)} ", end='', flush=True)
    submit_date = datetime.fromtimestamp(job["submit_timestamp"]).strftime('%Y-%m-%d_%H:%M')
    log_path = f"logs/{submit_date}_{job["task_id"]}_{job["retry_id"]}.log"
    if not os.path.isfile(log_path):
        log_url = f"https://firefoxci.taskcluster-artifacts.net/{job["task_id"]}/{job["retry_id"]}/public/logs/live_backing.log"
        log_response = requests.get(log_url)
        if log_response.ok:
            with open(log_path, "w") as log_file:
                log_file.write(log_response.text)
        else:
            print(f"Job {job["task_id"]} has no log (date: {datetime.fromtimestamp(job["submit_timestamp"])})")

print()
