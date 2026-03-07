# Home Inventory Manager

A professional Flask-based home inventory system to track items, serial numbers, locations, and storage boxes. Now updated with **User Authentication** and **Role-Based Access Control (RBAC)**.

## 📋 Features
- **User Authentication**: Secure login system for authorized access.
- **RBAC Support**:
  - **Admin**: Full access (Add, Edit, and Delete items).
  - **User**: Read-Only access (Viewing inventory only).
- **Enhanced Schema**: Tracks Serial Numbers (SN), Geo-location, and precise room placement.
- **Storage Logic**: Organize items inside specific Storage Boxes.
- **Dynamic Seeding**: Automatically creates default users and rooms (Guest room, Master room, etc.) on the first run.

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
- **Login Required**:
  - Enter your credentials to access the dashboard.
  - **Admin Account**: For managing inventory (write-access).
  - **User Account**: For viewing inventory (read-only).

### CLI Commands (Manage via Terminal)
Add items directly from your Raspberry Pi terminal:
```bash
# Format: flask add-item "Name" --sn "Serial" --cat "Category" --loc "Location"
docker exec home-inventory_web_1 flask add-item "Archer C20" --sn "SN12345" --cat "Electronics" --loc "drawing_room"
```

## 📋 Technology Stack
- **Backend**: Python (Flask), SQLAlchemy, Flask-Login
- **Database**: PostgreSQL (PostGIS ready)
- **Frontend**: Bootstrap 5 (Responsive UI)
- **Containerization**: Docker & Docker Compose
