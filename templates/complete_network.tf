
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "active_directory_vpc" {
  cidr_block = "192.168.0.0/16"

  tags = {
    Name = "ActiveDirectoryVPC"
  }
}

resource "aws_subnet" "active_directory_subnet" {
  vpc_id            = aws_vpc.active_directory_vpc.id
  cidr_block        = "192.168.1.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "ActiveDirectorySubnet"
  }
}

resource "aws_security_group" "domain_controller_sg" {
  vpc_id = aws_vpc.active_directory_vpc.id
  name   = "DomainControllerSecurityGroup"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["192.168.1.0/24"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "DomainControllerSecurityGroup"
  }
}

resource "aws_security_group" "workstation_sg" {
  vpc_id = aws_vpc.active_directory_vpc.id
  name   = "WorkstationSecurityGroup"

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["192.168.1.0/24"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "WorkstationSecurityGroup"
  }
}

resource "aws_instance" "domain_controller" {
  ami           = "ami-0abcdef1234567890" # Windows Server 2019 AMI ID (replace with actual AMI ID)
  instance_type = "t2.medium"             # Instance type with 2 vCPUs and 4 GB RAM
  subnet_id     = aws_subnet.active_directory_subnet.id

  vpc_security_group_ids = [aws_security_group.domain_controller_sg.id]

  tags = {
    Name = "DomainController"
  }

  root_block_device {
    volume_size = 100 # Storage: 100 GB
  }

  # Provisioning to setup the DC with PowerShell
  provisioner "remote-exec" {
    inline = [
      "powershell.exe -Command "Install-WindowsFeature AD-Domain-Services -IncludeManagementTools"",
      "powershell.exe -Command "Install-ADDSForest -CreateDnsDelegation:$false -DatabasePath 'C:\Windows\NTDS' -DomainMode 'WinThreshold' -DomainName 'example.com' -DomainNetbiosName 'EXAMPLE' -ForestMode 'WinThreshold' -InstallDns:$true -LogPath 'C:\Windows\NTDS' -NoRebootOnCompletion:$true -SysvolPath 'C:\Windows\SYSVOL' -Force:$true"",
      "powershell.exe -Command "Restart-Computer -Force""
    ]

    # Windows server settings for remote execution
    connection {
      type        = "winrm"
      host        = self.public_ip
      user        = "Administrator"
      password    = "password"
      insecure    = true
      timeout     = "2m"
    }
  }
}

resource "aws_instance" "workstation" {
  ami           = "ami-0123456789abcdef0" # Windows 10 Pro AMI ID (replace with actual AMI ID)
  instance_type = "t2.medium"             # Instance type with 2 vCPUs and 4 GB RAM
  subnet_id     = aws_subnet.active_directory_subnet.id

  vpc_security_group_ids = [aws_security_group.workstation_sg.id]

  tags = {
    Name = "Workstation"
  }

  root_block_device {
    volume_size = 100 # Storage: 100 GB
  }

  # Provisioning to join the workstation to the domain
  provisioner "remote-exec" {
    inline = [
      "powershell.exe -Command "Add-Computer -DomainName 'example.com' -Credential (Get-Credential -Username 'example.com\Administrator' -Message 'Password for the domain admin') -Restart -Force"",
    ]

    # Windows server settings for remote execution
    connection {
      type        = "winrm"
      host        = self.public_ip
      user        = "Administrator"
      password    = "password"
      insecure    = true
      timeout     = "2m"
    }
  }
}
