# File: README.md
# Flask API Demo with NGINX Reverse Proxy

This project deploys a Flask API with two backend instances (`flask-backend-1` and `flask-backend-2`) behind an NGINX reverse proxy on AWS, using Packer, Terraform/Terragrunt, and Ansible for infrastructure and configuration.

## Folder Structure
- `app/`: Flask API source code and Dockerfile.
- `packer/`: Packer configuration to build a custom AMI for the backend.
- `terraform/`: Terraform/Terragrunt code for AWS resources.
- `ansible/`: Ansible playbooks and roles for EC2 configuration.

## Prerequisites
- **AWS Credentials**: Configure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `~/.aws/credentials` or environment variables.
- **SSH Key Pair**: AWS EC2 key pair named `flask-demo` (e.g., `~/.ssh/flask-demo.pem`).
- **Tools**:
  - Terraform >= 1.8.0
  - Terragrunt >= 0.55.1
  - AWS CLI v2
  - Packer >= 1.10.0
  - Ansible
  - Docker
  - Python 3.9+
- **AWS Region**: `eu-west-1`

## Flask Backend
### Features
- Runs on two EC2 instances for redundancy and zero-downtime upgrades.
- In-memory storage (dictionary) for AWS Free Tier compatibility.
- Request validation using `reqparse` for required fields (`name`, `price`).
- Error handling with HTTP status codes (e.g., 400, 404).
- Listens on port `5001` for NGINX integration.
- Custom AMI built with Packer, including Docker and Flask configuration.

### Endpoints
- `GET /items`: List all items.
- `GET /item/<item_id>`: Retrieve an item by ID.
- `POST /item/<item_id>`: Create an item with `name` and `price`.
- `PUT /item/<item_id>`: Update or create an item.
- `DELETE /item/<item_id>`: Delete an item.

### Local Testing
1. Build and test the Flask API:
   ```bash
   cd app
   docker build -t flask-api .
   docker run -p 5001:5001 flask-api
   ```
2. Test endpoints:
   ```bash
   curl http://localhost:5001
   curl -X POST -H "Content-Type: application/json" -d '{"name":"Laptop","price":999.99}' http://localhost:5001/item/1
   curl http://localhost:5001/item/1
   ```

## Infrastructure Setup
### Terraform Deployment Order
Deploy resources in this order to respect dependencies:
1. `terraform/live/eu-west-1/flask-demo-vpc`
2. `terraform/live/eu-west-1/security-groups/nginx-proxy`
3. `terraform/live/eu-west-1/security-groups/flask-backend`
4. `terraform/live/eu-west-1/ami/amazon-linux-minimal`
5. `terraform/live/eu-west-1/ec2/flask-backend`
6. `terraform/live/eu-west-1/ec2/nginx-proxy`

Run in each directory:
```bash
terragrunt apply
```

### GitHub Actions Workflow
On pushes to `main` affecting `app/`, GitHub Actions:
1. Builds a new AMI with Packer (`build-ami.yml`).
2. Updates backend instances with the new AMI, ensuring zero downtime.
3. Configures instances and NGINX using Ansible (`deploy.yml`).

## Manual Deployment


### Step 1: Build and Store AMI
1. Build the AMI:
   ```bash
   cd packer
   packer init flask-backend.pkr.hcl
   packer validate flask-backend.pkr.hcl
   packer build flask-backend.pkr.hcl
   ```
2. Extract and store the AMI ID in SSM:
   ```bash
   AMI_ID=$(jq -r '.builds[-1].artifact_id' manifest.json | cut -d':' -f2)
   echo "AMI ID: $AMI_ID"
   aws ssm put-parameter \
     --name "/flask-demo/backend/latest-ami" \
     --value "$AMI_ID" \
     --type String \
     --overwrite \
     --region eu-west-1
   ```

### Step 2: Verify Ansible Inventory
```bash
cd ../ansible
python inventory_script.py
```
You should get a json output showing  groups of hosts.
### Step 3: Verify SSH Access
1. Access the NGINX proxy:
   ```bash
   ssh -i ~/.ssh/flask-demo.pem ubuntu@<nginx-proxy-public-ip>
   ```
2. From the NGINX proxy, access backend instances (using the private IPs from `inventory.yml`):
   ```bash
   ssh -i /home/ubuntu/.ssh/flask-demo.pem ec2-user@<flask-backend-1-private-ip>
   ssh -i /home/ubuntu/.ssh/flask-demo.pem ec2-user@<flask-backend-2-private-ip>
   ```

### Step 4: Update Backend Instances (Zero-Downtime)
1. **Route NGINX to `flask-backend-2`**:
   ```bash
   ansible-playbook -i inventory.yml playbook.yml \
     -e 'active_backends=[{"ip": "{{ hostvars['flask-backend-2'].ansible_host }}", "port": 5001}]'
   ```
   Verify NGINX configuration:
   ```bash
   ssh -i ~/.ssh/flask-demo.pem ubuntu@<nginx-proxy-public-ip> 'sudo cat /etc/nginx/conf.d/flask-backend.conf'
   ```
   Test the application:
   ```bash
   curl http://<nginx-proxy-public-ip>
   ```

2. **Update `flask-backend-1`**:
   ```bash
   cd ../terraform/live/eu-west-1/ec2/flask-backend
   terragrunt apply -auto-approve -target=module.ec2_instance.aws_instance.this[0]
   ```
   Verify the AMI:
   ```bash
   aws ec2 describe-instances --region eu-west-1 --filters "Name=tag:Name,Values=flask-backend-1" --query "Reservations[].Instances[].ImageId"
   ```
   Configure `flask-backend-1`:
   ```bash
   cd ../../../../ansible
   ansible-playbook -i inventory.yml playbook.yml --limit tag_Name_flask_backend_1
   ```
   Verify the container:
   ```bash
   ssh -i ~/.ssh/flask-demo.pem -J ubuntu@<nginx-proxy-public-ip> ec2-user@<flask-backend-1-private-ip> 'docker ps'
   ```

3. **Route NGINX to Both Backends**:
   ```bash
   ansible-playbook -i inventory.yml playbook.yml \
     -e 'active_backends=[{"ip": "{{ hostvars['flask-backend-1'].ansible_host }}", "port": 5001}, {"ip": "{{ hostvars['flask-backend-2'].ansible_host }}", "port": 5001}]'
   ```

4. **Route NGINX to `flask-backend-1`**:
   ```bash
   ansible-playbook -i inventory.yml playbook.yml \
     -e 'active_backends=[{"ip": "{{ hostvars['flask-backend-1'].ansible_host }}", "port": 5001}]'
   ```

5. **Update `flask-backend-2`**:
   ```bash
   cd ../terraform/live/eu-west-1/ec2/flask-backend
   terragrunt apply -auto-approve -target=module.ec2_instance.aws_instance.this[1]
   ```
   Configure `flask-backend-2`:
   ```bash
   cd ../../../../ansible
   ansible-playbook -i inventory.yml playbook.yml --limit tag_Name_flask_backend_2
   ```
   Verify the container:
   ```bash
   ssh -i ~/.ssh/flask-demo.pem -J ubuntu@<nginx-proxy-public-ip> ec2-user@<flask-backend-2-private-ip> 'docker ps'
   ```

6. **Restore NGINX to Both Backends**:
   ```bash
   ansible-playbook -i inventory.yml playbook.yml \
     -e 'active_backends=[{"ip": "{{ hostvars['flask-backend-1'].ansible_host }}", "port": 5001}, {"ip": "{{ hostvars['flask-backend-2'].ansible_host }}", "port": 5001}]'
   ```
   Test the application:
   ```bash
   curl http://<nginx-proxy-public-ip>
   ```

### Step 5: Test Initial Deployment
1. Generate inventory:
   ```bash
   cd ansible
   python3 inventory_script.py
   cat inventory.yml
   ```
2. Configure SSH key on NGINX proxy:
   ```bash
   ansible-playbook -i inventory.yml fetch-ssh-key.yml
   ```
3. Run the playbook:
   ```bash
   ansible-playbook -i inventory.yml playbook.yml -v
   ```
4. Verify Flask containers:
   ```bash
   ssh -i ~/.ssh/flask-demo.pem -J ubuntu@<nginx-proxy-public-ip> ec2-user@<flask-backend-1-private-ip> 'docker ps'
   ssh -i ~/.ssh/flask-demo.pem -J ubuntu@<nginx-proxy-public-ip> ec2-user@<flask-backend-2-private-ip> 'docker ps'
   ```
5. Verify NGINX configuration:
   ```bash
   ssh -i ~/.ssh/flask-demo.pem ubuntu@<nginx-proxy-public-ip> 'sudo cat /etc/nginx/conf.d/flask-backend.conf'
   ```
6. Test the application:
   ```bash
   curl http://<nginx-proxy-public-ip>
   ```

## Notes
- **Zero-Downtime**: The update process ensures one backend instance is always available.
- **Free Tier**: Uses `t2.micro` instances and `gp3` volumes (10GB for EC2, 16GB for Packer).
- **Troubleshooting**:
  - Check Terraform logs with `terragrunt plan`.
  - Verify Ansible inventory and SSH access.
  - Ensure `manifest.json` is generated by Packer.