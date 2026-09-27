# 🛡️ AIWAF — Adaptive AI-Based Web Application Firewall

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF)
![Deployment](https://img.shields.io/badge/Deployed-Render-46E3B7)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

AIWAF is a Web Application Firewall that uses Machine Learning instead of fixed rules to detect malicious web traffic in real time — classifying requests as safe or as SQL Injection, XSS, Path Traversal, or Command Injection using an ensemble of ML models.

## 🌐 Live Demo
https://aiwaf.onrender.com

## ✨ Features
- Real-time payload scanning
- Multi-model AI consensus (Logistic Regression, SVM, Random Forest)
- SQL Injection Detection
- XSS (Cross-Site Scripting) Detection
- Path Traversal Detection
- Command Injection Detection
- Simulated Login Page demo
- Adaptive retraining ("Retrain Neural Engine")
- Live confidence scoring per model

## 🖥 Dashboard
![Dashboard](dashboard.png)

## 🔐 Login Protection Demo
A simulated login form that runs every submitted username and password through the same AI detection engine before granting access.

<p float="left">
  <img src="login-demo.png" width="45%" />
  <img src="login-success.png" width="45%" />
</p>

## 📊 Scan Results
<p float="left">
  <img src="result1.png" width="45%" />
  <img src="result2.png" width="45%" />
</p>
<p float="left">
  <img src="result3.png" width="45%" />
  <img src="result4.png" width="45%" />
  <img src="result5.png" width="45%" />
</p>

## 🐳 DevOps Pipeline
- **Containerized** with Docker for consistent, portable deployment
- **CI/CD** via GitHub Actions — every push is automatically built and smoke-tested
- **Image Registry** — tested images published to GitHub Container Registry (GHCR)
- **Infrastructure as Code** — Terraform configuration included for AWS EC2 deployment
- **Continuous Deployment** to Render — auto-redeploys on every push to `main`

## 🛠 Tech Stack
- Python
- Flask
- scikit-learn
- pandas / numpy
- Docker
- GitHub Actions
- Terraform
- Render

## 👨‍💻 Author
Samala Deepak Kumar

© 2026 AIWAF
