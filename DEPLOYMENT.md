# ON1Builder Production Deployment Guide

This guide outlines the steps to deploy ON1Builder in a production environment with multi-chain support.

## 1. System Prerequisites

Install the required prerequisites:

```bash
./scripts/install_prereqs.sh
```

This script installs:
- Docker and Docker Compose
- HashiCorp Vault
- Other required dependencies

## 2. Vault Production Hardening

Set up HashiCorp Vault in production mode:

```bash
sudo cp deploy/vault.hcl /etc/vault.d/vault.hcl
sudo cp deploy/vault.service /etc/systemd/system/vault.service
sudo systemctl daemon-reload
sudo systemctl start vault
sudo systemctl enable vault
```

Initialize and configure Vault:

```bash
./scripts/vault_prod_init.sh
```

This script:
- Initializes Vault
- Unseals Vault
- Sets up a KV-v2 engine at secret/
- Creates policies and AppRoles
- Stores sensitive information securely

## 3. Environment Management

Generate the environment file:

```bash
./scripts/generate_env.sh
```

This script:
- Reads non-secret variables from .env.multi-chain.template
- Fetches secret values from Vault
- Creates a secure .env.multi-chain file

## 4. Containerization & Orchestration

Build and push the Docker image:

```bash
./scripts/build_and_push.sh
```

Deploy the containers:

```bash
sudo cp deploy/on1builder.service /etc/systemd/system/on1builder.service
sudo systemctl daemon-reload
sudo systemctl start on1builder
sudo systemctl enable on1builder
```

Or use Docker Compose directly:

```bash
docker-compose -f docker-compose.multi-chain.yml up -d
```

## 5. Secure Deployment

For a fully automated deployment, use the secure deployment script:

```bash
./secure_deploy_multi_chain.sh --go-live
```

This script:
- Verifies prerequisites
- Sets up Vault
- Generates environment files
- Builds and pushes Docker images
- Starts containers
- Verifies the deployment
- Imports Grafana dashboards
- Triggers a test alert

## 6. Verification & Monitoring

Verify the deployment:

```bash
./scripts/verify_live.sh
```

Access the Grafana dashboard at http://localhost:3000 with the default credentials:
- Username: admin
- Password: admin

Efter körning av deploy_prod.sh – se även [Post-Deployment Checklist](#post-deployment-checklist) för löpande drift.

## 7. Maintenance & Security

Set up automated maintenance tasks:

```bash
./scripts/cron_setup.sh
```

This script sets up cron jobs for:
- Daily PnL summary
- Gas price alerts
- Faucet balance checks
- Monthly wallet key rotation
- Weekly wallet key backups

## Post-Deployment Checklist

After deployment, ensure you complete the following tasks:

1. Change default Grafana admin password
2. Verify all chains are connected and active
3. Test alert notifications
4. Backup Vault unseal keys and root token
5. Schedule regular backups
6. Monitor system for 24 hours
7. Set up additional monitoring alerts

## Troubleshooting

If you encounter issues during deployment, check the logs:

```bash
# Check ON1Builder logs
docker-compose -f docker-compose.multi-chain.yml logs app

# Check Vault logs
sudo journalctl -u vault

# Check ON1Builder service logs
sudo journalctl -u on1builder
```

For more detailed troubleshooting, see the [Troubleshooting Guide](docs/TROUBLESHOOTING.md).
