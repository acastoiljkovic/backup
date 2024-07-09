#!/bin/bash

echo "127.0.0.1 localhost" > /etc/hosts

for vm in $(vagrant status --machine-readable | grep ",state,running" | cut -d, -f2); do
  VM_IP=$(vagrant ssh $vm -c "hostname -I" | tr -d '\r')

  if [ -z "$VM_IP" ]; then
    echo "Failed to retrieve IP address for $vm."
    exit 1
  fi

  echo "$VM_IP ${vm}" >> /etc/hosts
  echo "Hosts file updated with VM IP: $VM_IP ($vm)"
done