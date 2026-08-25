const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function fetchSummary() {
  const response = await fetch(`${API_BASE_URL}/summary`);
  if (!response.ok) {
    throw new Error(`Failed to fetch summary: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchPipeline() {
  const response = await fetch(`${API_BASE_URL}/pipeline`);
  if (!response.ok) {
    throw new Error(`Failed to fetch pipeline: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchRevenue() {
  const response = await fetch(`${API_BASE_URL}/revenue`);
  if (!response.ok) {
    throw new Error(`Failed to fetch revenue: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchOperations() {
  const response = await fetch(`${API_BASE_URL}/operations`);
  if (!response.ok) {
    throw new Error(`Failed to fetch operations: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchCrossBoard() {
  const response = await fetch(`${API_BASE_URL}/cross-board`);
  if (!response.ok) {
    throw new Error(`Failed to fetch cross-board: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchDataQuality() {
  const response = await fetch(`${API_BASE_URL}/data-quality`);
  if (!response.ok) {
    throw new Error(`Failed to fetch data quality: ${response.statusText}`);
  }
  return response.json();
}

export async function reloadData() {
  const response = await fetch(`${API_BASE_URL}/reload`, { method: "POST" });
  if (!response.ok) {
    throw new Error(`Failed to reload data: ${response.statusText}`);
  }
  return response.json();
}

export async function askSkylark(query: string) {
  const response = await fetch(`${API_BASE_URL}/ai/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) {
    throw new Error(`Failed to ask Skylark: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchLeadershipUpdate() {
  const response = await fetch(`${API_BASE_URL}/ai/leadership-update`);
  if (!response.ok) {
    throw new Error(`Failed to fetch leadership update: ${response.statusText}`);
  }
  return response.json();
}
