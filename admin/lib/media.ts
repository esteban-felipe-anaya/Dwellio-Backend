export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * Resolve a stored image value to a displayable URL.
 * - absolute (http/https/data) -> as-is
 * - relative `/media/...` upload path -> prefixed with the API base URL
 */
export function mediaUrl(path?: string | null): string {
  if (!path) return "";
  if (/^(https?:)?\/\//.test(path) || path.startsWith("data:")) return path;
  if (path.startsWith("/")) return `${API_BASE}${path}`;
  return `${API_BASE}/${path}`;
}
