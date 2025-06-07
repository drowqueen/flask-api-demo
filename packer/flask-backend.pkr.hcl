packer {
  required_plugins {
    amazon = {
      version = ">= 1.3.2"
      source  = "github.com/hashicorp/amazon"
    }
    docker = {
      version = ">= 1.0.8"
      source  = "github.com/hashicorp/docker"
    }
  }
}

source "amazon-ebs" "al2023-custom" {
  ami_name      = "custom-al2023-docker-flask-${formatdate("YYYYMMDDHHmmss", timestamp())}"
  instance_type = "t2.micro"
  region        = "eu-west-1"
  source_ami_filter {
    filters = {
      name                = "al2023-ami-2023.*-kernel-*-x86_64"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["amazon"]
  }
  ssh_username = "ec2-user"
  launch_block_device_mappings {
    device_name           = "/dev/xvda"
    volume_size           = 16
    volume_type           = "gp3"
    delete_on_termination = true
  }
}

build {
  sources = ["source.amazon-ebs.al2023-custom"]

  provisioner "shell" {
    inline = [
      "sudo dnf update -y",
      "sudo dnf install -y docker",
      "sudo systemctl enable --now docker",
      "sudo usermod -aG docker ec2-user",
      "sudo mkdir -p /opt/flask",
      "sudo chown -R ec2-user:ec2-user /opt/flask"
    ]
  }

  provisioner "file" {
    source      = "../app/"
    destination = "/opt/flask/"
  }

  provisioner "shell" {
    inline = [
      "sudo dnf update -y",
      "sudo dnf install -y docker",
      "sudo systemctl enable docker",
      "sudo systemctl start docker",
      "sudo usermod -a -G docker ec2-user",
      "cd /opt/flask",
      "if [ ! -f Dockerfile ]; then echo 'ERROR: Dockerfile not found in /opt/flask'; exit 1; fi",
      "if [ ! -f app.py ]; then echo 'ERROR: app.py not found in /opt/flask'; exit 1; fi",
      "sudo docker build -t flask-app-image:latest .",
      "sudo docker save -o /tmp/flask-app-image.tar flask-app-image:latest",
      "sudo mkdir -p /var/lib/docker/images",
      "sudo mv /tmp/flask-app-image.tar /var/lib/docker/images/",
      "sudo chown -R ec2-user:ec2-user /var/lib/docker/images",
      "sudo docker run -d --rm -p 5001:5001 --name flask-app flask-app-image:latest",
      "sleep 5",
      "curl -v http://localhost:5001",
      "sudo docker stop flask-app",
      "sudo docker system prune -af",
      "sudo rm -rf /var/cache/dnf/*"
    ]
  }

  post-processor "manifest" {
    output = "manifest.json"
  }
}