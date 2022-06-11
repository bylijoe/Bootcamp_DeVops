# Create a random id
#resource "random_id" "tf_bucket_id" {
#  byte_length = 2

#}

# Create Bucket S3
resource "aws_s3_bucket" "cicd_bucket" {
  bucket = "${var.bucket}"         #-${random_id.tf_bucket_id.dec}
  
   tags = {
        Name = "storage_s3"
        
  }
}
