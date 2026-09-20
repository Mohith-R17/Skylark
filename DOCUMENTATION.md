# Skylark
> Autonomous API Service

## 🚀 Features

* **Multi-Source Business Intelligence**: Seamlessly ingests business data across multiple source adapters (monday.com, Excel spreadsheets, or local in-memory storage) dynamically selected via environment variables.
* **AI-Driven Analytics**: Integrates an intelligent query engine enabling natural language analytics for pipeline management, revenue updates, operations metrics, and executive insights.
* **Real-time Data Reload & Synchronization**: Hot-reloading API endpoints allow background dataset refreshing on-demand without service downtime.
* **Interactive Executive Dashboard**: React/TypeScript dashboard delivering purpose-built views for Pipeline Overview, Leadership Updates, Data Health Audits, and AI Q&A.
* **Comprehensive Health & Observability**: Built-in operational monitoring endpoint tracking loaded deals, work orders, system timestamp, and active data source status.

## 📦 Tech Stack

* **Backend**: Python 3.10+, FastAPI, Pydantic, Asyncio, Python-dotenv, Uvicorn
* **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
* **Data Layer & Adapters**: REST Integration Services, pandas / openpyxl (Excel parsing), monday.com GraphQL API
* **State & Data Fetching**: Custom React Hooks with asynchronous API handlers

## 📡 API Reference

### System & Health Endpoints

#### Check API Health
```http
GET /health
```
**Response (200 OK):**
```json
{
  "status": "ok",
  "timestamp": "2026-03-31T12:00:00.000Z",
  "source": "monday.com",
  "deals_loaded": 150,
  "work_orders_loaded": 42
}
```

#### Reload Data Engine
```http
POST /api/reload
```
**Response (200 OK):**
```json
{
  "status": "reloaded",
  "deals": 150,
  "work_orders": 42
}
```

---

### Core Resource Endpoints

#### List Products
```http
GET /api/v1/products
```
**Response (200 OK):**
```json
[
  {
    "id": "prod_1001",
    "name": "Skylark Telemetry Suite",
    "category": "Analytics",
    "status": "active"
  }
]
```

#### Get Product Details
```http
GET /api/v1/products/{product_id}
```
**Response (200 OK):**
```json
{
  "id": "prod_1001",
  "name": "Skylark Telemetry Suite",
  "category": "Analytics",
  "status": "active"
}
```
**Response (404 Not Found):**
```json
{
  "detail": "Product not found"
}
```

#### Create User
```http
POST /api/v1/users
```
**Request Body:**
```json
{
  "name": "Alex Mercer",
  "email": "alex@skylarkdrones.com",
  "role": "analyst"
}
```
**Response (201 Created):**
```json
{
  "id": "usr_1001",
  "name": "Alex Mercer",
  "email": "alex@skylarkdrones.com",
  "role": "analyst"
}
```

#### Update User
```http
PUT /api/v1/users/{user_id}
```
**Request Body:**
```json
{
  "name": "Alex Mercer",
  "email": "alex@skylarkdrones.com",
  "role": "admin"
}
```
**Response (200 OK):**
```json
{
  "id": "usr_1001",
  "name": "Alex Mercer",
  "email": "alex@skylarkdrones.com",
  "role": "admin"
}
```

#### Delete User
```http
DELETE /api/v1/users/{user_id}
```
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
* Node.js 18.x or higher
* npm or pnpm

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/skylark.git
   cd skylark
   ```

2. **Set up the Backend environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file inside the `backend` directory:
   ```env
   DATA_SOURCE=monday  # Options: monday, excel, inmemory
   MONDAY_API_KEY=your_monday_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Set up Frontend dependencies:**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the App

1. **Start the FastAPI Backend server:**
   ```bash
   cd backend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   The backend API will be available at `http://localhost:8000`. OpenAPI documentation is available at `http://localhost:8000/docs`.

2. **Start the React Frontend development server:**
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend UI will be accessible at `http://localhost:5173`.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request