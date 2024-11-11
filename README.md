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


## ✨ Features

### 🔍 Advanced Analysis
- Static and dynamic malware analysis
- Supports multiple file formats
- Extracts file's metadata dynamically 
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
  

## 🏗️ Architecture


### Core Components

mermaid
graph TD
A[Client] --> B[FastAPI Server]
B --> C[File Processing]
C --> D[S3 Storage]
C --> E[Analysis Queue]
E --> F[VM Workers]
F --> G[Results DB]


### File Processing Flow

1. **Upload** - Secure file reception and validation
2. **Storage** - S3 storage with deduplication
3. **Analysis** - Distributed processing across workers
4. **Results** - Centralized result aggregation

## 📚 API Reference

### Analysis Endpoints


## 🔒 Security

### Cryptographic Security
- Ed25519 signatures for worker authentication
- Secure key management
- PEM format key storage

### File Safety


## 🛠️ Development

### Project Structure

cordguard/
├── app.py # Application entry
├── routes/ # API endpoints
├── cordguard_core.py # Core functionality
├── cordguard_database.py # Database operations
└── cordguard_utils.py # Utility functions

### Environment Variables

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ENDPOINT_URL_S3=your_s3_endpoint
AWS_REGION=your_region
BUCKET_NAME_S3=your_bucket_name
```


## 🤝 Contributing

We eagrly waiting to receive your contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for more details.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- Security Team (security@cordguard.org)

## 🙏 Acknowledgments

- SurrealDB
- FastAPI
- AWS S3
- Tigirs Storage
---

<div align="center">

Made with ❤️ by the CordGuard Team

[Website](https://cordguard.org) • 
[Documentation](https://docs.cordguard.org) • 
[Report Bug](https://github.com/CordGuard/cordguard-backend/issues)

</div>
