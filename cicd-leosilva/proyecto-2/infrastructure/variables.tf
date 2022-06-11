variable "project_name" {
  type        = map
  description = "Name of the project."
  default     = {
    dev  = "acme-storage-dev"
    prod = "acme-storage-prod"
  }
}


variable "aws_region" {
  
}

variable "env" {
  description = "env: dev or prod"
}