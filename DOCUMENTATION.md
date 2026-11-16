# Skylark
> Autonomous API Service

## 🚀 Features

* **Multi-Source Data Integration:** Automatically switches data sources dynamically between monday.com APIs, local Excel spreadsheets, and fallback in-memory adapters based on environment configuration.
* **AI-Powered Business Intelligence:** Leverages an embedded AI engine to provide founder-facing analytics, executive updates, and natural language Q&A ("Ask Skylark").
* **Data Health & Pipeline Monitoring:** Tracks operations, work orders, sales pipeline, revenue stats, and data quality across board integrations.
* **Unified REST API:** Built with FastAPI to deliver low-latency endpoints (avg 1ms response time) supporting real-time dashboard visualization.
* **Interactive Dashboard Frontend:** A modern React and TypeScript web client featuring executive overviews, data health diagnostics, and automated leadership reporting.

## 📦 Tech Stack

### Backend
* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Validation & Settings:** Pydantic, python-dotenv
* **Server:** Uvicorn

### Frontend
* **Framework:** React 18
* **Language:** TypeScript
* **Build Tool:** Vite
* **Styling:** Tailwind CSS

## 📡 API Reference

### Health & Operations

#### `GET /health`
Returns the operational status, current data adapter source, and record metrics.

**Response Example:**
```json
{
  "status": "ok",
  "timestamp": "2026-03-31T20:00:00.000000",
  "source": "monday",
  "deals_loaded": 42,
  "work_orders_loaded": 18
}
```

#### `POST /api/reload`
Triggers an immediate reload of underlying datasets from the configured adapter source.

**Response Example:**
```json
{
  "status": "reloaded",
  "deals": 42,
  "work_orders": 18
}
```

---

### Core Resource Management

#### `GET /api/v1/products`
Retrieves a list of active products and associated pipeline metrics.

**Response Example:**
```json
[
  {
    "id": "prod_1001",
    "name": "Drone Inspection Kit",
    "category": "Hardware",
    "status": "active"
  }
]
```

#### `POST /api/v1/users`
Creates a new user record in the system.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "role": "analyst"
}
```

**Response Example:**
```json
{
  "id": "usr_1001",
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "role": "analyst",
  "created_at": "2026-03-31T20:05:00Z"
}
```

#### `PUT /api/v1/users/{user_id}`
Updates existing details for a specified user.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "role": "lead_analyst"
}
```

**Response Example:**
```json
{
  "id": "usr_1001",
  "name": "Jane Doe",
  "role": "lead_analyst",
  "updated_at": "2026-03-31T20:10:00Z"
}
```

#### `DELETE /api/v1/users/{user_id}`
Deletes a user account by their unique ID.

**Response Example:**
```json
{
  "status": "deleted",
  "id": "usr_9999"
}
```

## 🛠️ Getting Started

### Prerequisites

* **Python:** v3.10 or higher
* **Node.js:** v18.0.0 or higher
* **Package Manager:** `npm` or `yarn`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/skylark.git
   cd skylark
   ```

2. **Set up Backend Environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Frontend Dependencies:**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Environment Configuration:**
   Create a `.env` file in the `backend` directory:
   ```env
   DATA_SOURCE=monday # Options: monday, excel, inmemory
   MONDAY_API_TOKEN=your_token_here
   ```

### Running the App

1. **Start the Backend Service:**
   ```bash
   cd backend
   uvicorn app:app --reload --port 8000
   ```
   The backend API will be available at `http://localhost:8000`.

2. **Start the Frontend Development Server:**
   ```bash
   cd frontend
   npm run dev
   ```
   The application UI will be accessible at `http://localhost:5173`.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request