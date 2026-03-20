#!/bin/bash
# ============================================================================
#  RabbitMQ Federation Setup Script (Linux)
# ============================================================================
#  Node: pc10
#  IP: 192.168.1.19
#  Hostname: pc10.local
#  Location: Office - Room 10
#  Generated: 2026-03-20 09:39:20
# ============================================================================

set -e  # Exit on error

GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================================================${NC}"
echo -e " RabbitMQ Federation Setup - pc10 (192.168.1.19)"
echo -e "${CYAN}============================================================================${NC}"
echo ""

# Check if RabbitMQ is installed
if ! command -v rabbitmqctl &> /dev/null; then
    echo -e "${RED}[ERROR] rabbitmqctl not found!${NC}"
    echo "Please install RabbitMQ first: https://rabbitmq.com/download.html"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} RabbitMQ found"
echo ""

# Step 1: Enable federation plugin
echo -e "${BLUE}[STEP 1/3]${NC} Enabling federation plugin..."
rabbitmq-plugins enable rabbitmq_federation
echo -e "${GREEN}[OK]${NC} Federation plugin enabled"
echo ""

# Step 2: Setup upstreams
echo -e "${BLUE}[STEP 2/3]${NC} Setting up federation upstreams..."
echo ""

# Upstream: pc1 (192.168.1.10)
echo -e "  Adding upstream: pc1 -> 192.168.1.10"
rabbitmqctl set_parameter federation-upstream pc1 \
  '{"uri":"amqp://guest:guest@192.168.1.10:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc1 added"
echo ""

# Upstream: pc2 (192.168.1.11)
echo -e "  Adding upstream: pc2 -> 192.168.1.11"
rabbitmqctl set_parameter federation-upstream pc2 \
  '{"uri":"amqp://guest:guest@192.168.1.11:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc2 added"
echo ""

# Upstream: pc3 (192.168.1.12)
echo -e "  Adding upstream: pc3 -> 192.168.1.12"
rabbitmqctl set_parameter federation-upstream pc3 \
  '{"uri":"amqp://guest:guest@192.168.1.12:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc3 added"
echo ""

# Upstream: pc4 (192.168.1.13)
echo -e "  Adding upstream: pc4 -> 192.168.1.13"
rabbitmqctl set_parameter federation-upstream pc4 \
  '{"uri":"amqp://guest:guest@192.168.1.13:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc4 added"
echo ""

# Upstream: pc5 (192.168.1.14)
echo -e "  Adding upstream: pc5 -> 192.168.1.14"
rabbitmqctl set_parameter federation-upstream pc5 \
  '{"uri":"amqp://guest:guest@192.168.1.14:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc5 added"
echo ""

# Upstream: pc6 (192.168.1.15)
echo -e "  Adding upstream: pc6 -> 192.168.1.15"
rabbitmqctl set_parameter federation-upstream pc6 \
  '{"uri":"amqp://guest:guest@192.168.1.15:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc6 added"
echo ""

# Upstream: pc7 (192.168.1.16)
echo -e "  Adding upstream: pc7 -> 192.168.1.16"
rabbitmqctl set_parameter federation-upstream pc7 \
  '{"uri":"amqp://guest:guest@192.168.1.16:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc7 added"
echo ""

# Upstream: pc8 (192.168.1.17)
echo -e "  Adding upstream: pc8 -> 192.168.1.17"
rabbitmqctl set_parameter federation-upstream pc8 \
  '{"uri":"amqp://guest:guest@192.168.1.17:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc8 added"
echo ""

# Upstream: pc9 (192.168.1.18)
echo -e "  Adding upstream: pc9 -> 192.168.1.18"
rabbitmqctl set_parameter federation-upstream pc9 \
  '{"uri":"amqp://guest:guest@192.168.1.18:5672/", \
   "exchange":"chat_exchange", \
   "ack-mode":"on-confirm", \
   "max-hops":1, \
   "prefetch-count":100}'
echo -e "${GREEN}  [OK]${NC} Upstream pc9 added"
echo ""

# Step 3: Setup federation exchange
echo -e "${BLUE}[STEP 3/3]${NC} Setting up federation exchange..."
rabbitmqctl set_parameter federation-exchange chat_exchange \
  '{"upstream-set":"all"}'
echo -e "${GREEN}[OK]${NC} Federation exchange configured"
echo ""

# Verification
echo -e "${CYAN}============================================================================${NC}"
echo -e " Setup Complete!"
echo -e "${CYAN}============================================================================${NC}"
echo ""
echo "Node Information:"
echo "  - Name: pc10"
echo "  - IP: 192.168.1.19"
echo "  - Hostname: pc10.local"
echo "  - Location: Office - Room 10"
echo ""
echo "Federation Summary:"
echo "  - Exchange: chat_exchange"
echo "  - Upstreams configured: 9"
echo "  - Cluster: chat_federation"
echo ""
echo "Next Steps:"
echo "  1. Start RabbitMQ: sudo systemctl start rabbitmq-server"
echo "  2. Run docker-compose up -d"
echo "  3. Verify: rabbitmqctl list_parameters"
echo ""

# List configured parameters
echo "Configured Parameters:"
echo "----------------------"
rabbitmqctl list_parameters
echo ""

echo -e "${GREEN}✓ Federation setup complete for pc10!${NC}"
