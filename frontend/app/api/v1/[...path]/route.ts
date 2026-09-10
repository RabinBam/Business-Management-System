import { NextRequest, NextResponse } from "next/server";
export const dynamic = "force-dynamic";
async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const base = process.env.INTERNAL_API_URL || "http://127.0.0.1:8000/api/v1";
  const url = `${base}/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;
  try {
    const headers = new Headers();
    for (const name of ["content-type", "x-admin-key"]) {
      const value = request.headers.get(name); if (value) headers.set(name, value);
    }
    const response = await fetch(url, {
      method: request.method, headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
      cache: "no-store", redirect: "error",
    });
    return new NextResponse(response.body, { status: response.status,
      headers: { "Content-Type": response.headers.get("content-type") || "application/json", "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ success: false, error: { code: "BACKEND_UNAVAILABLE",
      message: "The backend is starting or unavailable. Run Start-Byapari and retry once both services are healthy." } }, { status: 503 });
  }
}
export { proxy as GET, proxy as POST, proxy as PUT, proxy as DELETE, proxy as PATCH };
