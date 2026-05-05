const API_BASE = "http://127.0.0.1:9000/api";

function getLoggableBody(body) {
  if (!body || typeof body !== "string") {
    return body ?? "";
  }

  try {
    return JSON.parse(body);
  } catch {
    return body;
  }
}

export async function api(path, options = {}) {
  const url = `${API_BASE}${path}`;
  console.log(`[API REQUEST] ${options.method || "GET"} ${url}`, getLoggableBody(options.body));

  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = typeof payload === "string" ? payload : payload.message || "Request failed";
    console.error(`[API ERROR] ${response.status} ${response.statusText} - ${message}`);
    throw new Error(message);
  }

  console.log("[API RESPONSE]", payload);
  return payload;
}
