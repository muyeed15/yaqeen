import * as http from "http";
import * as https from "https";

/**
 * Node's bundled `fetch` (undici) can crash the whole server process with an
 * uncatchable `AssertionError: !this.paused` in `Parser.finish` when the
 * upstream closes the connection (`Connection: close` / FIN) while the HTTP
 * parser is paused under backpressure (responses larger than ~64 KiB). Django's
 * dev server and Gunicorn's sync workers both close connections eagerly, so
 * SSR / Route Handler requests to the backend can trigger it.
 *
 * Routing backend calls through Node's core `http`/`https` client avoids the
 * undici parser entirely. Only URLs pointing at `DJANGO_API_URL` are diverted;
 * every other request uses the original (Next-patched) `fetch`.
 */
const PATCH_FLAG = "__yaqeenBackendFetchPatched__";

function normalizeRequestHeaders(headers: HeadersInit | undefined): http.OutgoingHttpHeaders {
  if (!headers) return {};
  if (typeof Headers !== "undefined" && headers instanceof Headers) {
    const out: Record<string, string> = {};
    headers.forEach((value, key) => {
      out[key] = value;
    });
    return out;
  }
  if (Array.isArray(headers)) return Object.fromEntries(headers);
  return { ...(headers as Record<string, string>) };
}

function toBuffer(body: RequestInit["body"] | undefined): Buffer | undefined {
  if (body == null) return undefined;
  if (typeof body === "string") return Buffer.from(body);
  if (Buffer.isBuffer(body)) return body;
  if (body instanceof Uint8Array) return Buffer.from(body);
  return undefined;
}

function backendFetch(input: string, init?: RequestInit): Promise<Response> {
  const url = new URL(input);
  const lib = url.protocol === "https:" ? https : http;
  const requestBody = toBuffer(init?.body);

  const headers = normalizeRequestHeaders(init?.headers);
  // WSGI servers (Django's dev server, Gunicorn sync workers) do not read
  // chunked request bodies. Node's http client only sets a body length when we
  // provide it, so set Content-Length explicitly; otherwise POST bodies are
  // silently dropped.
  if (requestBody) {
    const hasContentLength = Object.keys(headers).some(
      (key) => key.toLowerCase() === "content-length",
    );
    const hasTransferEncoding = Object.keys(headers).some(
      (key) => key.toLowerCase() === "transfer-encoding",
    );
    if (!hasContentLength && !hasTransferEncoding) {
      headers["Content-Length"] = String(requestBody.byteLength);
    }
  }

  return new Promise<Response>((resolve, reject) => {
    const req = lib.request(
      url,
      {
        method: init?.method ?? "GET",
        headers,
      },
      (res) => {
        const chunks: Buffer[] = [];
        res.on("data", (chunk: Buffer) => chunks.push(chunk));
        res.on("end", () => {
          const responseHeaders = new Headers();
          for (const [key, value] of Object.entries(res.headers)) {
            if (typeof value === "string") responseHeaders.set(key, value);
            else if (Array.isArray(value)) responseHeaders.set(key, value.join(", "));
          }
          resolve(
            new Response(Buffer.concat(chunks), {
              status: res.statusCode ?? 500,
              statusText: res.statusMessage,
              headers: responseHeaders,
            }),
          );
        });
        res.on("error", reject);
      },
    );

    req.on("error", reject);
    if (requestBody) req.write(requestBody);
    req.end();
  });
}

function registerBackendFetchPatch(): void {
  const globalWithFlag = globalThis as typeof globalThis & { [PATCH_FLAG]?: boolean };
  if (globalWithFlag[PATCH_FLAG]) return;

  const backendBase = process.env.DJANGO_API_URL;
  if (!backendBase) return;

  const originalFetch = globalThis.fetch.bind(globalThis);

  globalThis.fetch = ((input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const rawUrl =
      typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
    if (rawUrl.startsWith(backendBase)) {
      return backendFetch(rawUrl, init);
    }
    return originalFetch(input, init);
  }) as typeof fetch;

  globalWithFlag[PATCH_FLAG] = true;
}

registerBackendFetchPatch();
