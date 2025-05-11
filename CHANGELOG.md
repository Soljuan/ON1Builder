# Changelog

## v1.0.0 (2023-05-11)

### 🚀 Features

- **Multi-Chain Support**: Added support for running on multiple EVM-compatible chains simultaneously
- **Slack Notifications**: Implemented alert sending via SlackNotifier
- **Transaction Simulation**: Added transaction simulation functionality
- **Secure Deployment**: Enhanced deployment process with Vault integration
- **Monitoring**: Added Prometheus and Grafana dashboards for multi-chain monitoring

### 🔧 Improvements

- **Documentation**: Updated README.md and DEPLOYMENT.md with multi-chain usage instructions
- **Testing**: Added comprehensive tests for multi-chain functionality
- **Error Handling**: Improved error handling and logging
- **Security**: Enhanced security with proper secret management

### 🐛 Bug Fixes

- Fixed nonce management issues in multi-chain transactions
- Resolved race conditions in worker initialization
- Fixed environment variable handling in Docker containers

### 📝 Documentation

- Added post-deployment checklist
- Updated installation instructions for multi-chain setup
- Added Swedish references for deployment process
