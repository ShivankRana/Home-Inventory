# Home Inventory Manager

A professional Flask-based home inventory system to track items, serial numbers, locations, and storage boxes.

## 📋 Configuration

Create a `.env` file in the project root to configure the database data path:

```bash
DB_DATA_PATH=/data2/postgres_data/home-inventory
```

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
- **Access:** `http://<YOUR_PI_IP>:8082`

### CLI Commands
Add items directly from your Raspberry Pi terminal:
```bash
docker exec home-inventory_web_1 flask add-item "Archer C20" --sn "SN12345" --cat "Electronics" --loc "drawing_room"
```
