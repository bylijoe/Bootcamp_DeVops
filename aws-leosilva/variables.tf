# Variables

variable "aws_acces_key" {
    description = "Clave de acceso"
    type = string
    default = ""
}
variable "aws_secret_key" {
    description = "Clave de acceso secreta"
    type = string
    default = ""
}

variable "aws_region" {
    description = "Nombre de la region por defecto"
    type = string
    default = "eu-west-1"
  
}

variable "bonus-vpc" {
    description = "El nombre de la vpc a crear"
    type    = string
    default = "bonus-vpc"
}

variable "vpc-cidr" {
    description = "La dirección de red de la vpc a crear"
    type    = string
    default = "10.0.0.0/16"
}

variable "igw-bonus" {
    description = "Nombre del Internet Gateway"
    type    = string
    default = "bonus-igw"
}

variable "private-subnet1-bonus" {
    description = "Nombre de la subred privada 1"
    type    = string
    default = "private-subnet1"
}

variable "private-subnet1-cidr" {
    description = "Rango de direcciones de la subred privada 1"
    type    = string
    default = "10.0.13.0/24"
}

variable "private-subnet2-bonus" {
    description = "Nombre de la subred privada 2"
    type    = string
    default = "private-subnet2"
}

variable "private-subnet2-cidr" {
    description = "Rango de direcciones de la subred privada 2"
    type    = string
    default = "10.0.14.0/24"
}

variable "public-subnet1-bonus" {
    description = "Nombre de la subred publica 1"
    type    = string
    default = "public-subnet1"
}

variable "public-subnet1-cidr" {
    description = "Rango de direcciones de la subred pública 1"
    type    = string
    default = "10.0.3.0/24"
}

variable "public-subnet2-bonus" {
    description = "Nombre de la subred publica 2"
    type    = string
    default = "public-subnet2"
}

variable "public-subnet2-cidr" {
    description = "Rango de direcciones de la subred publica 2"
    type    = string
    default = "10.0.4.0/24"
}

variable "route-table-public-subnet1-bonus" {
    description = "Nombre de la tabla de rutas para la subred publica"
    type    = string
    default = "route-table-public-subnet1"
}

variable "route-table-public-subnet2-bonus" {
    description = "Nombre de la tabla de rutas para la subred publica"
    type    = string
    default = "route-table-public-subnet2"
}


variable "db_subnet_group" {
    description = "subnet group para rds"
    type = string
    default = "subnet group"
}
