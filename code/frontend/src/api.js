const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  return response.json();
}

export function listDocuments() {
  return request("/api/documents");
}

export function getDocument(id) {
  return request(`/api/documents/${id}`);
}

export function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/api/documents", { method: "POST", body: formData });
}

export function searchSentences(query, threshold) {
  return request("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, threshold }),
  });
}
