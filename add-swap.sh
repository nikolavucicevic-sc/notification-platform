#!/bin/bash
# Script to add swap space to EC2 instance
# Run this on your EC2 instance as root: sudo bash add-swap.sh

set -e

echo "=========================================="
echo "Adding Swap Space to EC2 Instance"
echo "=========================================="

# Check if swap already exists
if swapon --show | grep -q '/swapfile'; then
    echo "⚠️  Swap already exists:"
    swapon --show
    echo ""
    read -p "Do you want to remove and recreate it? (y/N): " response
    if [[ "$response" != "y" && "$response" != "Y" ]]; then
        echo "Exiting..."
        exit 0
    fi
    echo "Removing existing swap..."
    swapoff /swapfile
    rm -f /swapfile
fi

# Create 2GB swap file
SWAP_SIZE=2G
echo "Creating ${SWAP_SIZE} swap file..."
fallocate -l ${SWAP_SIZE} /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048

# Set correct permissions
echo "Setting permissions..."
chmod 600 /swapfile

# Make it a swap file
echo "Making swap file..."
mkswap /swapfile

# Enable swap
echo "Enabling swap..."
swapon /swapfile

# Verify
echo ""
echo "✓ Swap enabled successfully!"
echo ""
echo "Current swap status:"
swapon --show
echo ""
free -h

# Make it permanent
echo ""
echo "Making swap permanent across reboots..."
if ! grep -q '/swapfile' /etc/fstab; then
    echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
    echo "✓ Added to /etc/fstab"
else
    echo "✓ Already in /etc/fstab"
fi

# Optimize swap settings
echo ""
echo "Optimizing swap settings..."
echo "vm.swappiness=10" | tee -a /etc/sysctl.conf
echo "vm.vfs_cache_pressure=50" | tee -a /etc/sysctl.conf
sysctl -p

echo ""
echo "=========================================="
echo "✓ Swap configuration complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "- Swap size: ${SWAP_SIZE}"
echo "- Swappiness: 10 (less aggressive swapping)"
echo "- Persistent across reboots: Yes"
echo ""
echo "Next step: Restart Docker containers"
echo "  cd ~/notification-platform"
echo "  docker compose down"
echo "  docker compose up -d"
