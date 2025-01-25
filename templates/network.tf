
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
