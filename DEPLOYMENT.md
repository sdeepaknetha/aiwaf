# AIWAF — DevOps Pipeline

This adds containerization, CI/CD, and infra-as-code around the existing AIWAF Flask app.

## 1. Where these files go

Drop these into the root of your `AIWAF/` project (same level as `requirements.txt`):

```
AIWAF/
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── DEPLOYMENT.md
├── .github/workflows/ci-cd.yml
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── app/
├── data/
├── models/
├── logs/
└── requirements.txt
```

## 2. Run it locally with Docker

```bash
docker compose up --build
```

Visit `http://localhost:5000`. Logs and any `/api/feedback` data land in `./logs` and `./data`
on your host (mounted as volumes), so they survive container restarts.

Note: the original code runs Flask with `debug=True`. The Dockerfile instead runs it through
`gunicorn`, which is what you'd use in any real deployment — debug mode with a public port is a
security risk (it exposes an interactive debugger).

## 3. CI/CD — what the GitHub Actions workflow does

`.github/workflows/ci-cd.yml` runs on every push/PR to `main`:
1. Builds the Docker image
2. Boots it and hits `/` as a smoke test (catches "image builds but app crashes on start" bugs)
3. On a push to `main` only: logs into GitHub Container Registry (GHCR) and pushes the image,
   tagged both `latest` and with the short commit SHA

No extra secrets needed — it uses the built-in `GITHUB_TOKEN`. Just make sure the repo's
**Settings → Actions → General → Workflow permissions** allows "Read and write permissions"
(needed to push to GHCR).

Your image ends up at: `ghcr.io/<your-github-username>/<repo-name>:latest`

## 4. Deploying the image

Pick based on how much infra you want to manage:

**Easiest — Render / Railway (free tier, no servers to manage)**
- Create a new Web Service, point it at your GitHub repo
- It'll detect the Dockerfile and build automatically
- Set the port to `5000`

**More "DevOps resume" points — AWS EC2 via Terraform**
The `terraform/` folder provisions an EC2 instance, installs Docker, and pulls your image
straight from GHCR:

```bash
cd terraform
terraform init
terraform apply \
  -var="key_pair_name=<your-ec2-key-pair>" \
  -var="my_ip_cidr=<your-ip>/32" \
  -var="ghcr_repo=<your-username>/<repo-name>"
```

Terraform prints the public IP / URL when done. Destroy with `terraform destroy` when finished
(avoid leaving it running and racking up AWS charges).

**Important:** make your GHCR package public first (GitHub repo → Packages → your image →
Package settings → Change visibility), otherwise the EC2 `docker run` in `user_data` will fail
to pull it without auth.

## 5. What this demonstrates (for your resume/interviews)

- **Containerization**: Dockerfile, multi-layer caching, `.dockerignore` hygiene
- **CI**: automated build + smoke test on every push
- **CD**: automated image publish to a container registry
- **IaC**: Terraform provisioning cloud infra instead of manual console clicks
- This is exactly the Docker → CI/CD → Terraform chain that came up in your D&B interview
