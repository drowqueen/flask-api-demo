# File: README.md
# Ansible and Terragrunt Demo with a Simple RESTful API Backend, NAT instance and NGINX Reverse Proxy

This project deploys a minimalistic Flask API with two backend instances (`flask-backend-1` and `flask-backend-2`) behind an NGINX reverse proxy on AWS,  using Terraform/Terragrunt, and Ansible for infrastructure and configuration.
Backend instances are in a private subnet and go throught the nat instance to download necessary packages.

## Notes
- **Free Tier**: Uses `t2.micro` instances and `gp3` volumes

## Planned features

* Fully automated tests incorporated into github actions
* Zero downtime upgrade of flask backend 


## Folder Structure
- `app/`: Flask API source code and Dockerfile.
- `terraform/`: Terraform/Terragrunt code for AWS resources.
- `ansible/`: Ansible playbooks and roles for EC2 configuration.

## Prerequisites
- **AWS Credentials**: Configure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `~/.aws/credentials` or environment variables.
- **SSH Key Pair**: AWS EC2 key pair named `flask-demo` (e.g., `~/.ssh/flask-demo.pem`).
- **Tools**:
  - Terraform >= 1.8.0
  - Terragrunt >= 0.55.1
  - AWS CLI v2
  - Ansible
  - Docker
  - Python 3.9+
- **AWS Region**: `eu-west-1`

**NOTE:** Private subnet where nat instance sits needs to be associated with the proper route table, otherwise backends will not be able to download packages.

## Flask Backend
### Features
- Runs on two EC2 instances for redundancy and zero-downtime upgrades.
- In-memory storage (dictionary) for AWS Free Tier compatibility.
- Request validation using `reqparse` for required fields (`name`, `price`).
- Error handling with HTTP status codes (e.g., 400, 404).
- Listens on port `5001` for NGINX integration.

### Endpoints
- `GET /items`: Retrieve a JSON object containing all items.
- `GET /item/<item_id>`: Retrieve an item by ID.
- `POST /item/<item_id>`: Create a new item with the given item_id. Requires JSON body with name (string) and price (float).
    Fails if the item already exists.
- `PUT /item/<item_id>`: Update an existing item or create it if it doesn’t exist. Requires JSON body with name and price.
- `DELETE /item/<item_id>`: Delete an item.
- `PATCH /item/<item_id>`: Partially update fields of an existing item. Provide JSON body with any subset of name and/or price.

### Local Testing
1. Build and test the Flask API:
   ```bash
   cp .env.example .env
   pip install -r requirements.txt
   cd app
   docker build -t flask-api .
   docker run -p 5001:5001 flask-api
   ```
2. Test the endpoints and the API:
   ```bash
   curl http://localhost:5001
   <repo_root>/tests/api-test.sh
   ```

## Infrastructure Setup
### Terraform Deployment Order
Deploy resources in this order to respect dependencies:
1. `terraform/live/eu-west-1/flask-demo-vpc`
2. `terraform/live/eu-west-1/security-groups/nginx-proxy`
3. `terraform/live/eu-west-1/security-groups/flask-backend`
4. `terraform/live/eu-west-1/iam/*`
5. `terraform/live/eu-west-1/ec2/flask-backend`
6. `terraform/live/eu-west-1/ec2/nginx-proxy`
7. `terraform/live/eu-west-1/ec2/nat-instance`
8. `terraform/live/eu-west-1/ec2/nat-route`

Run in each directory:
```bash
terragrunt apply
```

## GitHub Actions Workflows

### deploy.yml
- Checks out the repository.
- Sets up Python 3.9 environment.
- Installs dependencies including pytest and requests.
- Runs the unit tests (pytest tests/test_app.py).
- Optionally, builds and tests the Docker image.
- Reports test results and fails the workflow if any tests fail.

This ensures continuous integration and automated validation of the Flask backend code before deployment.

### terragrunt-plan.yml

- Checks out the repository with full git history.
- Sets up AWS credentials for Terragrunt access.
- Installs and configures Terragrunt CLI.
- Caches Terragrunt cache directory to speed up repeated runs.
- Detects which Terragrunt directories have changed based on .tf and .hcl file diffs.
- Runs terragrunt plan in each changed directory with non-interactive and detailed output.
- Reports any planned infrastructure changes or errors.
- Detects the cumulative changes since the branch diverged from main.

### terragrunt-apply.yml
¨
Same steps as the terragrunt-plan workflow, but it applies the cumulative changes pushed
to the branch since it diverged from main.

## Manual Deployment and Testing

### Step 1: Verify Ansible Inventory
```bash

ansible/inventory_script.py
```
You should get a json output showing  groups of hosts.

### Step 2: Bootstrap and deploy the configurations and apps
   ```bash
   ansible-playbook -i ansible/inventory_script.py ansible/playbooks/deploy_all.yml  
   ```

### Step 3:  Verify everything is working

1. Verify ssh access to the NGINX proxy:
   ```bash
   ssh -i ~/.ssh/flask-demo.pem ubuntu@<nginx-proxy-public-ip>
   ```

2. Verify Flask containers:
   ```bash
   ssh -i ~/.ssh/flask-demo.pem -J ubuntu@<nginx-proxy-public-ip> ec2-user@<flask-backend-1-private-ip> 'docker ps'
   ssh -i ~/.ssh/flask-demo.pem -J ubuntu@<nginx-proxy-public-ip> ec2-user@<flask-backend-2-private-ip> 'docker ps'
   ```

3. Test the application:
   ```bash
   curl http://<nginx-proxy-public-ip>
   <repo_root>/pytest tests/test_app.py
   ```
