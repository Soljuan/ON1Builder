# ON1Builder

ON1Builder is a fully-automated, production-grade, multi-chain trading bot running on Ethereum Mainnet and Polygon Mainnet.

## Features

- Multi-chain support for Ethereum Mainnet and Polygon Mainnet
- Secure secret management with HashiCorp Vault
- Comprehensive monitoring with Prometheus and Grafana
- Alerting via Slack and email
- Automated maintenance and security tasks
- Production-grade deployment with Docker and systemd

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ON1Builder.git
   cd ON1Builder
   ```

2. Copy the multi-chain environment template:
   ```bash
   cp .env.multi-chain.template .env.multi-chain
   ```

3. Edit the `.env.multi-chain` file to configure your multi-chain settings:
   ```bash
   nano .env.multi-chain
   ```

4. Run the secure deployment script:
   ```bash
   ./secure_deploy_multi_chain.sh
   ```

5. Follow the prompts to enter sensitive information.

6. Verify the deployment:
   ```bash
   ./scripts/verify_live.sh
   ```

## Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [Security Guidelines](SECURITY.md)
- [Post-Deployment Checklist](DEPLOYMENT.md#post-deployment-checklist)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
