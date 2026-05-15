# FleetDM Azure Slack Alerting System
A containerized FleetDM monitoring and alerting solution deployed on an Azure Virtual Machine using Docker Compose.
This project integrates FleetDM policy monitoring with automated Slack notifications to improve endpoint visibility and compliance monitoring.

## Features
- Deploys FleetDM using Docker Compose
- Multi-container architecture with:
  - FleetDM
  - MySQL
  - Redis
- Custom Python alerting service
- Real-time Slack alerts for failing FleetDM policies
- Automated policy compliance monitoring
- Deduplication logic to prevent repeated alerts
- Persistent Docker volumes for data storage
- Environment-based configuration management
- Linux-based cloud deployment on Azure VM

## Architecture

```text
+--------------------------------------------------+
|                   Azure VM                       |
|                Ubuntu / Linux                    |
+--------------------------------------------------+

                    Docker Compose
                           |
    ---------------------------------------------------
    |                    |                    |
    v                    v                    v

+-----------+      +-----------+      +------------------+
|   MySQL   |      |   Redis   |      |     FleetDM      |
| Database  |      |  Cache    |<---->|   API Server     |
+-----------+      +-----------+      +------------------+
                                                  ^
                                                  |
                                                  |
                                     +-------------------------+
                                     |     fleet-alerts        |
                                     |  Python Alert Service   |
                                     +-------------------------+
                                                  |
                                                  v
                                        +----------------+
                                        | Slack Webhook  |
                                        | Notifications  |
                                        +----------------+
```


## Technologies Used
- Azure Virtual Machine
- Docker
- Docker Compose
- FleetDM
- Python
- MySQL
- Redis
- Slack Webhooks / Slack API
- Linux Administration
- REST APIs
- Bash / Shell Scripting

## Project Structure
```
fleetdm-slack-alerting/
├── docker-compose.yml
├── README.md
├── .env.example
├── .gitignore
│
├── fleet-alerts/
│   ├── Dockerfile
│   ├── fleet_alerts.py
│   ├── requirements.txt
│
└── secrets/ (optional - NOT committed)
    ├── fleet-mdm-win-wstep.cert
    └── fleet-mdm-win-wstep.key
```


## Docker Services

- FleetDM
  - Endpoint visibility and policy management
- MySQL
  - Stores FleetDM application data
- Redis
  - Caching and queue management
- fleet-alerts
  - Custom Python monitoring service
  - Polls FleetDM APIs
  - Sends Slack alerts for failing policies

 ## Example Slack Alert
 ```
🚨 Fleet Policy Alert (2026-05-15 10:00:00 UTC)

Policy                      | Platform | Failing
--------------------------- | -------- | --------
Disk Encryption Enabled     | macOS    | 5
Antivirus Running           | Windows  | 3
Firewall Enabled            | macOS    | 2
```

## Future Improvements
- Add Grafana dashboards
- Kubernetes deployment support
- Email alert integration
- Prometheus monitoring
- CI/CD pipeline integration using GitHub Actions

## 👨‍💻 Author
```
Oshadhi Wickramasinghe
DevOps Engineer
Sri Lanka
```
