#variables

variable "aws_region" {
    description = "Nombre de la region por defecto"
    type        = string
    default     = "eu-west-1"
  
}

variable "bucket" {
    description = "Nombre bucket s3"
    type        = string
    default     = ""
}