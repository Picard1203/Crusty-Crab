# The Krusty Crab — Restaurant Order Management API

SpongeBob SquarePants themed restaurant order management system built with FastAPI and MongoDB.

## Quick Start

### Step 1: Start MongoDB (replica set required for transactions)

```bash
docker-compose up -d
```

To stop:
```bash
docker-compose down
```

To stop and wipe data:
```bash
docker-compose down -v
```

### Step 2: Configure environment

```bash
cp .env.example .env
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start the API

```bash
python main.py
# or
uvicorn src.app:app --reload
```

API docs available at: `http://localhost:8000/docs`

## Running Tests

```bash
pytest -v
```

## User Roles

| Role | Permissions |
|------|-------------|
| `guest` | Create orders, view own order status |
| `worker` | Update order statuses |
| `administrator` | View profits/statistics, manage menu, manage users |
