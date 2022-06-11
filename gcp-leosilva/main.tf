terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.8.0"
    }
  }
}
provider "google" {

  credentials = file("cred-mod2.json")
  
  project = var.project_name
  region  = var.region_name
  zone    = var.zone_name
}

resource "google_compute_network" "vpc_network" {
  name = "gpc-network"
}
resource "google_compute_address" "vm_static_ip" {
  name = "gpc-static-ip"  
}

resource "google_compute_firewall" "http" {
  name    = "fw-http"
  network = google_compute_network.vpc_network.id

  allow {
    protocol = "tcp"
    ports    = ["80", "3306"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "ssh" {
  name    = "fw-ssh"
  network = google_compute_network.vpc_network.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_instance" "vm_instance" {
  depends_on = [
    google_compute_address.vm_static_ip
  ]  
    
  name         = "gpc-vm-machine"
  machine_type = var.machine_type
  
  boot_disk {
    initialize_params {
      image = var.image_name
    }
  }
  network_interface {
      network = google_compute_network.vpc_network.name
    access_config {
        nat_ip = google_compute_address.vm_static_ip.address
    }
  }
  metadata_startup_script =  "sudo apt-get update && sudo apt-get install apache2 -y"
  tags = ["htp-server"]
}

resource "random_string" "name" {
    length = 8
    special = false
    upper =  false 
  
}

 resource "google_storage_bucket" "bucket" {
   name = "mideposito2-${random_string.name.result}"
   location = var.region_name
   storage_class = "standard" 
   
 }

resource "google_sql_database_instance" "instance" {
  name             = "mysql-mod2-db1"
  region           = var.region_name
  database_version = "MYSQL_5_7"
  settings {
    tier = "db-f1-micro"

     backup_configuration {
      enabled            = true
      start_time         = "12:30"
      binary_log_enabled = true
    }
  }
    
  
}
resource "google_sql_database" "google" {
  name      = "google"
  instance  = google_sql_database_instance.instance.name
  charset   = "utf8"
  collation = "utf8_general_ci"
}
resource "google_sql_database" "cloud" {
  name      = "cloud"
  instance  = google_sql_database_instance.instance.name
  charset   = "utf8"
  collation = "utf8_general_ci"
}
resource "google_sql_user" "users" {
  name     = "alumno"
  instance = google_sql_database_instance.instance.name
  password = "googlecloud"
}  
