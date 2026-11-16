# Skylark
> Autonomous API Service

## 🚀 Features

* **AI-Powered Business Intelligence:** Founder-facing analytics engine delivering pipeline, revenue, and operational insights for Skylark Drones.
* **Flexible Data Adapters:** Automatic multi-source data ingestion prioritizing monday.com integration, Excel spreadsheet parsing, and in-memory mock data fallback.
* **Natural Language Queries:** Interactive "Ask Skylark" intelligence assistant backed by a custom AI service.
* **Data Health & Governance:** Real-time data audit screens and deal validation to ensure report accuracy and consistency.
* **Automated Leadership Updates:** One-click summary compilation designed for high-level executive updates and cross-board visibility.

## 📦 Tech Stack

* **Backend:** Python 3.10+, FastAPI, Pydantic, Uvicorn, Python-Dotenv
* **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
* **Services & Ingestion:** DataService adapter pattern (monday.com API, Excel/Pandas), AIService

## 📡 API Reference

### Health & Operations

#### `GET /health`
Returns system status, active data adapter, and telemetry on loaded entity metrics.

**Response (200 OK):**
```json
{
  "status": "ok",
  "timestamp": "2026-03-30T12:00:00Z",
  "source": "monday.com",
  "deals_loaded": 142,
  "work_orders_loaded": 88
}
```

#### `POST /api/reload`
Triggers an on-demand re-fetch of data from the configured data source.

**Response (200 OK):**
```json
{
  "status": "reloaded",
  "deals": 142,
  "work_orders": 88
}
```

---

### Products & Resource Endpoints

#### `GET /api/v1/products`
Retrieves a list of available drone hardware, software modules, and service products.

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": "prod_1001",
      "name": "Skylark Enterprise Fleet License",
      "category": "Software",
      "price": 15000.00
    },
    {
      "id": "prod_1002",
      "name": "Autonomous Survey Drone Unit",
      "category": "Hardware",
      "price": 8500.00
    }
  ]
}
```

#### `GET /api/v1/products/{id}`
Retrieves detailed information for a specific product by ID.

**Response (404 Not Found):**
```json
{
  "detail": "Product prod_not_found not found"
}
```

---

### User Management Endpoints

#### `POST /api/v1/users`
Creates a new user profile in the system.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@skylark.com",
  "role": "analyst"
}
```

**Response (201 Created):**
```json
{
  "id": "usr_1001",
  "name": "Jane Doe",
  "email": "jane.doe@skylark.com",
  "role": "analyst",
  "created_at": "2026-03-30T12:00:00Z"
}
```

#### `PUT /api/v1/users/{id}`
Updates an existing user's profile details.

**Request Body:**
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@skylark.com",
  "role": "lead_analyst"
}
```

**Response (200 OK):**
```json
{
  "id": "usr_1001",
  "name": "Jane Doe",
  "email": "jane.doe@skylark.com",
  "role": "lead_analyst",
  "updated_at": "2026-03-30T12:05:00Z"
}
```

#### `DELETE /api/v1/users/{id}`
Deletes a user profile by ID.

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User usr_9999 successfully deleted"
}
```

## 🛠️ Getting Started

### Prerequisites

* Python 3.10 or higher
* Node.js 18.x or higher and npm (or yarn/pnpm)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/skylark.git
   cd skylark
   ```

2. **Set up the Backend environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   MONDAY_API_TOKEN=your_monday_token_here
   EXCEL_FILE_PATH=data/skylark_bi.xlsx
   ```

4. **Set up the Frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the App

1. **Start the API Backend service:**
   ```bash
   uvicorn backend.app:app --reload --port 8000
   ```
   The API will be available at `http://localhost:8000`. You can access interactive Swagger docs at `http://localhost:8000/docs`.

2. **Start the Frontend development server:**
   ```bash
   cd frontend
   npm run dev
   ```
   The UI will be accessible at `http://localhost:5173`.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)