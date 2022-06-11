#!/bin/bash

#Julián García-Sotoca

if [ $# -eq 1 ]
then
  echo "$1 min to wait"
  SECONDS=($1*60)
  echo "$SECONDS seconds"
  until [ $SECONDS -eq 0 ]; do
    ((--SECONDS))
    echo $SECONDS
    sleep 1
  done
else
  echo "One argument is needed and only one"
  exit 1
fi
exit 0 
