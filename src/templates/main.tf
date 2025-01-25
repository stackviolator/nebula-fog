provider "aws" {
  region = "us-east-1"
}

resource "random_password" "admin_password" {
  length           = 16
  special          = true
  upper            = true
  lower            = true
  number           = true
  override_special = "!@#$%^&*()-_=+[]{}<>?"
}

resource "aws_instance" "windows_ad" {
  ami           = "ami-0b2f6494ff0b07a0e"  # Windows Server 2019 AMI ID (example)
  instance_type = "t2.large"
  key_name      = "nebula-fog-hackathon-keypair"

  network_interface {
    associate_public_ip_address = true
    subnet_id                   = "subnet-12345678"  #we need a subnet > got stuck here 
  }

  tags = {
    Name = "Windows-AD"
  }

  user_data = <<-EOF
    <powershell>
    # Set admin password
    net user Administrator "${random_password.admin_password.result}" /Y

    # Install Active Directory services
    Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools

    # Promote to Domain Controller
    Import-Module ADDSDeployment
    Install-ADDSForest `
      -DomainName "example.com" `
      -SafeModeAdministratorPassword (ConvertTo-SecureString "${random_password.admin_password.result}" -AsPlainText -Force) `
      -Force
    </powershell>
  EOF
}

resource "aws_eip" "windows_ad_eip" {
  instance = aws_instance.windows_ad.id
}

resource "aws_security_group" "windows_sg" {
  name_prefix = "windows-ad-sg"

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # RDP access
  }

  ingress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]  # DNS
  }

  ingress {
    from_port   = 88
    to_port     = 88
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Kerberos
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allow all outbound traffic
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "admin_password" {
  value     = random_password.admin_password.result
  sensitive = true
}
