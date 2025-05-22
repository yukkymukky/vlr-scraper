#!/bin/bash

# get username from arg
if [ -z "$1" ]; then
  echo "Usage: $0 <username>"
  exit 1
fi

USERNAME=$1

# check if json file with username exists 
if [ -f "${USERNAME}_wrapped.json" ]; then
  echo "File ${USERNAME}_wrapped.json already exists. Do you want to delete it? (y/n)"
  read -r answer
  if [ "$answer" != "y" ]; then
    echo "Exiting without deleting the file."
    exit 0
  fi
  # delete the file
  echo "Deleting ${USERNAME}_wrapped.json"
  rm -f "${USERNAME}_wrapped.json"
fi

# run scrapy spider
echo "Running scrapy spider for username: $USERNAME"
scrapy crawl vlr -a username=$USERNAME