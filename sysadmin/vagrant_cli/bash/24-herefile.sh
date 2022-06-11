#!/bin/bash

cat << token
content to be used as command's standard input
token

cat << EOF > myconffile.conf
parameter1=one
parameter2=two
EOF

cat myconffile.conf