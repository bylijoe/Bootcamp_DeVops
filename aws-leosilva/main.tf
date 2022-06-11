# Configure the AWS Provider

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  
  access_key = "${var.aws_acces_key}"
  secret_key = "${var.aws_secret_key}" 
  region = "${var.aws_region}"
}

# Create a VPC

resource "aws_vpc" "bonus-vpc" {
  cidr_block = "10.0.0.0/16"

  enable_dns_support = true
  enable_dns_hostnames = true
  
   tags = {
    Name = var.bonus-vpc
  }

}

# Recoger zonas de disponibilidad disponibles

data "aws_availability_zones" "available" {
  state = "available"
}

# Subnet privada 1 (eu-west-a)

resource "aws_subnet" "private-subnet1" {
  vpc_id     = "${aws_vpc.bonus-vpc.id}"
  availability_zone = "${data.aws_availability_zones.available.names[0]}"
  cidr_block = var.private-subnet1-cidr

  tags = {
    Name = var.private-subnet1-bonus
  }
}

# Subnet privada 2 (eu-west-b)

resource "aws_subnet" "private-subnet2" {
  vpc_id     = "${aws_vpc.bonus-vpc.id}"
  availability_zone = "${data.aws_availability_zones.available.names[1]}"
  cidr_block = var.private-subnet2-cidr

  tags = {
    Name = var.private-subnet2-bonus
  }
}

# Subnet publica 1 (eu-west-a)

resource "aws_subnet" "public-subnet1" {
  vpc_id     = "${aws_vpc.bonus-vpc.id}"
  availability_zone = "${data.aws_availability_zones.available.names[0]}"
  cidr_block = var.public-subnet1-cidr
  map_public_ip_on_launch = true # auto-assing public ip
  
  tags = {
    Name = var.public-subnet1-bonus
  }
}

# Subnet publica 2 (eu-west-b)

resource "aws_subnet" "public-subnet2" {
  vpc_id     = "${aws_vpc.bonus-vpc.id}"
  availability_zone = "${data.aws_availability_zones.available.names[1]}"
  cidr_block = var.public-subnet2-cidr
  map_public_ip_on_launch = true # auto-assing public ip
  
  tags = {
    Name = var.public-subnet2-bonus
  }
}

# IGW

resource "aws_internet_gateway" "igw" {
  vpc_id = "${aws_vpc.bonus-vpc.id}" 

  tags = {
    Name = var.igw-bonus
  }
}

# Tabla de rutas para la subred pública 1

resource "aws_route_table" "route-table-public-subnet1" {
  vpc_id = "${aws_vpc.bonus-vpc.id}"
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.igw.id}"
  }
  tags = {
    Name = var.route-table-public-subnet1-bonus
  }
}

resource "aws_route_table_association" "route-table-association-public-subnet1" {
  subnet_id      = "${aws_subnet.public-subnet1.id}"
  route_table_id = "${aws_route_table.route-table-public-subnet1.id}"
}

# Tabla de rutas para la subred pública 2

resource "aws_route_table" "route-table-public-subnet2" {
  vpc_id = "${aws_vpc.bonus-vpc.id}"
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.igw.id}"
  }
  tags = {
    Name = var.route-table-public-subnet2-bonus
  }
}

resource "aws_route_table_association" "route-table-association-public-subnet2" {
  subnet_id      = "${aws_subnet.public-subnet2.id}"
  route_table_id = "${aws_route_table.route-table-public-subnet2.id}"
}

# Tabla de rutas para la subred privada 1 

resource "aws_route_table" "route-table-private-subnet1" {
  vpc_id = "${aws_vpc.bonus-vpc.id}"
  tags = {
    Name = "route-table-private-subnet1"
  }
}

resource "aws_route_table_association" "route-table-association-private-subnet1" {
  subnet_id      = "${aws_subnet.private-subnet1.id}"
  route_table_id = "${aws_route_table.route-table-private-subnet1.id}"
}

# Tabla de rutas para la subred privada 2 

resource "aws_route_table" "route-table-private-subnet2" {
  vpc_id = "${aws_vpc.bonus-vpc.id}"
  
  tags = {
    Name = "route-table-private-subnet2"
  }
}

resource "aws_route_table_association" "route-table-association-private-subnet2" {
  subnet_id      = "${aws_subnet.private-subnet2.id}"
  route_table_id = "${aws_route_table.route-table-private-subnet2.id}"
}

# Segurity groups RDS

resource "aws_security_group" "group_rds" {
  name   = "Security group rds "
  vpc_id = "${aws_vpc.bonus-vpc.id}"
  
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = ["${aws_security_group.group_for_instance.id}"]

  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]

  }

}

# RDS
# Subnets Groups

resource "aws_db_subnet_group" "db-subnet" {
  name       = "db-subnet"
  subnet_ids = ["${aws_subnet.private-subnet1.id}", "${aws_subnet.private-subnet2.id}"]
}

# Instance  DDBBB

resource "aws_db_instance" "rds-bonus" {
  allocated_storage = 20
  identifier = "bonus-mysql-ddbb"
  storage_type = "gp2"
  engine = "mysql"
  engine_version = "8.0.27"
  instance_class = "db.t2.micro"
  db_subnet_group_name = "${aws_db_subnet_group.db-subnet.name}"
  db_name = "remember2"
  skip_final_snapshot= true
  username = "admin"
  password = "practica"
  port = "3306"
      
}

# Security group EC2

resource "aws_security_group" "group_for_instance" {
  name = "security group ec2"
  vpc_id = "${aws_vpc.bonus-vpc.id}"

  ingress {
    from_port   = 8080          
    to_port     = 8080
    protocol    = "tcp"
    security_groups = ["${aws_security_group.elb_asg.id}"]
  }
  ingress {
    from_port   = 22         
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   #replace it with your ip addres
  }

  egress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # problemas para referenciar  ["${aws_security_group.group_rds_id}"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]

  }
 
  lifecycle {
    create_before_destroy = true
  }
}

# Security group Load Balancer

resource "aws_security_group" "elb_asg" {
  name = "security group LB"
  vpc_id = "${aws_vpc.bonus-vpc.id}"

  
  ingress  {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # problemas para referenciar  ["${aws_security_group.group_for_instance.id}"]
    
  } 
}

# Target group

resource "aws_lb_target_group" "tg-bonus" {
  name     = "lb-tg-bonus"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "${aws_vpc.bonus-vpc.id}"
  load_balancing_algorithm_type = "round_robin"
  deregistration_delay = 60
  stickiness {
    enabled = false
    type    = "lb_cookie"
    cookie_duration = 60
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
    path                = "/api/utils/healthcheck"
    protocol            = "HTTP"
    matcher             = 200
    
  }
  lifecycle {
   create_before_destroy = true
  }

}

# Load Balancer

resource "aws_lb" "appln-lb" {
  name               = "bonus-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["${aws_security_group.elb_asg.id}"]
  subnets            = ["${aws_subnet.public-subnet1.id}", "${aws_subnet.public-subnet2.id}"]
  enable_deletion_protection = false
  depends_on = [ aws_lb_target_group.tg-bonus]
  
}

output "alb-endpoint" {
  value = aws_lb.appln-lb.dns_name
} 

resource "aws_lb_listener" "listner" {
  
  load_balancer_arn = aws_lb.appln-lb.id
  port              = 80
  protocol          = "HTTP"
default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = " Site Not Found"
      status_code  = "200"
   }
}
    
  depends_on = [  aws_lb.appln-lb ]
}

resource "aws_lb_listener_rule" "rule" {
    
  listener_arn = aws_lb_listener.listner.id
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg-bonus.arn
  }

  condition {
    host_header {
      values = ["version2.anandg.xyz"]
    }
  }
}

# Configuracion instancia 

resource "aws_launch_configuration" "lc-appweb" {
  image_id          = "ami-0db188056a6ff81ae"
  instance_type     = "t2.micro" 
  security_groups   = ["${aws_security_group.group_for_instance.id}"]
  associate_public_ip_address = true
  user_data         = <<-EOF
				#!/bin/bash
				sudo yum update -y
        sudo yum install -y docker
        sudo service docker start
        sudo docker run -d --name rtb -p 8080:8080 vermicida/rtb
				EOF


  lifecycle {
    create_before_destroy = true
  }
}

# ASG

resource "aws_autoscaling_group" "asg-bonus" {

  name                    = "bonus-autoscalingGroup"
  launch_configuration    = aws_launch_configuration.lc-appweb.id
  health_check_type       = "EC2"
  min_size                = 1
  max_size                = 1
  desired_capacity        = 1
  vpc_zone_identifier     = ["${aws_subnet.public-subnet1.id}", "${aws_subnet.public-subnet2.id}"]
  target_group_arns       = ["${aws_lb_target_group.tg-bonus.arn}"]
  tag {
    key = "Name"
    propagate_at_launch = true
    value = "bonus-instancia"
  }

  lifecycle {
    create_before_destroy = true
  }
}