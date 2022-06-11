#!/bin/sh

size=$(aws s3 ls s3://acme-storage-prod-kc --recursive --human-readable --summarize | grep "Total Size" | awk '{print $3}')
# El tamaño obtenido es en MiB

# Converter string to int
sizenum= expr $size

if [ $sizenum => 20 ]; then  # If Result >= 20MiB Clean Bucket
  aws s3 rm s3://acme-storage-prod-kc --recursive
fi