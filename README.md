# Home Inventory Manager

A professional Flask-based home inventory system to track items, serial numbers, locations, and storage boxes.

## 🛠️ Installation (Local Pi)

1. **Clone the repository:**
   ```bash
   git clone git@github.com:ShivankRana/Home-Inventory.git
   cd Home-Inventory
   ```

2. **Start with Docker:**
   Ensure you have Docker and Docker Compose installed, then run:
   ```bash
   docker-compose up -d --build
   ```

## 🚀 How to Execute

### Web Interface
- **Direct Access:** `http://<YOUR_PI_IP>:8082`
- **Via Proxy Manager:** `http://inventory.local` (Requires `/etc/hosts` update on your PC).

### CLI Commands (Manage via Terminal)
Add items directly from your Raspberry Pi terminal:
```bash
# Format: flask add-item "Name" --sn "Serial" --cat "Category" --loc "Location"
docker exec home-inventory_web_1 flask add-item "Archer C20" --sn "SN12345" --cat "Electronics" --loc "drawing_room"
```

## 📋 Features
- **Enhanced Schema:** Tracks Serial Numbers (SN), Geo-location, and precise room placement.
- **Storage Logic:** Organize items inside specific Storage Boxes.
- **Dynamic Seeding:** Automatically creates rooms (Guest room, Master room, etc.) on first run.
