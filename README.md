# 🛡️ CordGuard - Backend

<div align="center">

<img src="cordguard-assets/logo.png" width="150" height="150" style="border-radius: 10px;" alt="CordGuard Logo">

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)](LICENSE)

*A distributed malware analysis system with secure file analysis through REST API*

[Getting Started](#-getting-started) •
[Features](#-features) •
[Architecture](#%EF%B8%8F-architecture) •
[API Reference](#-api-reference) •
[Security](#-security)

</div>

---

## 📋 Table of Contents
- [🚀 Getting Started](#-getting-started)
- [✨ Features](#-features)
- [🔒 Security](#-security)
- [🛠️ Development](#️-development)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👥 Team](#-team)
- [🚀 Deployment](#-deployment)
- [🙏 Acknowledgments](#-acknowledgments)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- SurrealDB
- AWS S3 compatible storage
- Requires environment variables (see below)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/cordguard/cordguard.git
   cd cordguard
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```
d

## ✨ Features

### 🔍 Advanced Analysis
- Static and dynamic malware analysis
- Supports multiple file formats
- Extracts file metadata dynamically 
- Distributed processing across VM workers

### 🏗️ Robust Architecture
- FastAPI-powered REST API
- S3 integration for secure storage
- SurrealDB for data persistence
- Asynchronous task processing

### 🔐 Security First
- Ed25519 cryptographic signatures
- Secure file handling
- Memory-safe operations
- Path traversal prevention



## 🔒 Security

### Cryptographic Security
- Ed25519 signatures for worker authentication
- Secure key management
- PEM format key storage

### File Safety
- Secure file uploads
- Validation and deduplication before analysis


## 🛠️ Development

### Environment Variables
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ENDPOINT_URL_S3=your_s3_endpoint
AWS_REGION=your_region
BUCKET_NAME_S3=your_bucket_name

OPENAI_API_KEY=your_openai_api_key

SURREALDB_USERNAME=your_surrealdb_username
SURREALDB_PASSWORD=your_surrealdb_password
SURREALDB_URL=your_surrealdb_url

REGISTRY_HOST=
API_HOST=
WORKER_HOST=
AI_API_HOST=
USERS_HOST=
API_KEY=
WORKER_API_KEY=
REGISTRY_API_KEY=
AI_API_KEY=

PORT=
```


## 🤝 Contributing

We eagerly await your contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for more details.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 👥 Team

- Security Team (security@cordguard.org)


## 🚀 Deployment

Deploy with Fly.io:
```bash
fly deploy
```


## 🙏 Acknowledgments

- SurrealDB
- FastAPI
- AWS S3
- Tigirs Storage
- Fly.io

---

<div align="center">

Made with ❤️ by the CordGuard Team

[Website](https://cordguard.org) • 
[Documentation](https://docs.cordguard.org) • 
[Report Bug](https://github.com/CordGuard/cordguard-backend/issues)

</div>