/**
 * API Service for communicating with Rag Innovations FastAPI backend (Railway / Localhost).
 */

const rawBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE = rawBase.replace(/\/+$/, '');

/**
 * Send a user message to the RAG backend.
 * @param {string} message - User question
 * @returns {Promise<{answer: string, sources: Array, status: string}>}
 */
export async function sendChatMessage(message) {
  // Support both /chat and /api/chat endpoints
  const primaryUrl = `${API_BASE}/chat`;
  const fallbackUrl = `${API_BASE}/api/chat`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 45000); // 45s timeout for LLM

  try {
    let response = await fetch(primaryUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
      signal: controller.signal,
    });

    if (response.status === 404) {
      response = await fetch(fallbackUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
        signal: controller.signal,
      });
    }

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail ||
        errorData.answer ||
        `Server responded with HTTP ${response.status}: ${response.statusText}`
      );
    }

    const data = await response.json();
    return {
      answer: data.answer || "I received an empty response. Please try rephrasing your question.",
      sources: data.sources || [],
      status: data.status || "success",
    };
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error("Request timed out while generating a response. Please try again.");
    }
    console.error("API error:", err);
    throw err;
  }
}

/**
 * Check backend health & diagnostic status.
 * @returns {Promise<{status: string, vectorstore_loaded: boolean, llm_loaded: boolean, model_name: string}>}
 */
export async function checkBackendHealth() {
  const primaryUrl = `${API_BASE}/health`;
  const fallbackUrl = `${API_BASE}/api/health`;

  try {
    let response = await fetch(primaryUrl, { headers: { 'Accept': 'application/json' } });
    if (response.status === 404) {
      response = await fetch(fallbackUrl, { headers: { 'Accept': 'application/json' } });
    }
    if (!response.ok) {
      return { status: 'offline', vectorstore_loaded: false, llm_loaded: false };
    }
    return await response.json();
  } catch {
    return { status: 'offline', vectorstore_loaded: false, llm_loaded: false };
  }
}
