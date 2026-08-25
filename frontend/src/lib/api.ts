const API_BASE_URL = import.meta.env.VITE_API_URL || "https://skylark-twhf.onrender.com";

export async function fetchSummary() {
  const response = await fetch(`${API_BASE_URL}/api/summary`);
  if (!response.ok) {
    throw new Error(`Failed to fetch summary: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchPipeline() {
  const response = await fetch(`${API_BASE_URL}/api/pipeline`);
  if (!response.ok) {
    throw new Error(`Failed to fetch pipeline: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchRevenue() {
  const response = await fetch(`${API_BASE_URL}/api/revenue`);
  if (!response.ok) {
    throw new Error(`Failed to fetch revenue: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchOperations() {
  const response = await fetch(`${API_BASE_URL}/api/operations`);
  if (!response.ok) {
    throw new Error(`Failed to fetch operations: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchCrossBoard() {
  const response = await fetch(`${API_BASE_URL}/api/cross-board`);
  if (!response.ok) {
    throw new Error(`Failed to fetch cross-board: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchDataQuality() {
  const response = await fetch(`${API_BASE_URL}/api/data-quality`);
  if (!response.ok) {
    throw new Error(`Failed to fetch data quality: ${response.statusText}`);
  }
  return response.json();
}

export async function reloadData() {
  const response = await fetch(`${API_BASE_URL}/api/reload`, { method: "POST" });
  if (!response.ok) {
    throw new Error(`Failed to reload data: ${response.statusText}`);
  }
  return response.json();
}

export async function askSkylark(query: string) {
  const response = await fetch(`${API_BASE_URL}/api/ai/ask`, {
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
  const response = await fetch(`${API_BASE_URL}/api/ai/leadership-update`);
  if (!response.ok) {
    throw new Error(`Failed to fetch leadership update: ${response.statusText}`);
  }
  return response.json();
}
