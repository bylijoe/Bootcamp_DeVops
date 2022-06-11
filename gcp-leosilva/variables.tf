variable "project_name" {
 
  description = "The name of the project to instanciate the instance at."
  default     = "mod2-gcp"
}

variable "region_name" {
 
  description = "The region that this terraform configuration will instanciate ."
  default     = "europe-west2"
}

variable "zone_name" {
  
  description = "The zone that this terraform configuration will instanciate ."
  default     = "europe-west2-c"
}

variable "machine_type" {
 
  description = "The size that this instance will be."
  default     = "f1-micro"
}

variable "image_name" {
 
  description = "The kind of VM this instance will become"
  default     = "ubuntu-os-cloud/ubuntu-1804-bionic-v20190403"
}