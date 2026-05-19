import { NextRequest, NextResponse } from "next/server";

const PUBLIC_ROUTES = ["/login", "/register"];
const DEFAULT_PROTECTED = "/dashboard";
const DEFAULT_PUBLIC = "/login";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const refreshToken = request.cookies.get("refresh_token")?.value;

  // Middleware не має доступу до localStorage, тому перевіряємо cookie.
  // Якщо refresh_token є в cookie — вважаємо авторизованим.
  // Детальна перевірка access token відбувається в AuthProvider на клієнті.
  const isAuthenticated = !!refreshToken;
  const isPublicRoute = PUBLIC_ROUTES.some((r) => pathname.startsWith(r));

  if (!isAuthenticated && !isPublicRoute) {
    return NextResponse.redirect(new URL(DEFAULT_PUBLIC, request.url));
  }

  if (isAuthenticated && isPublicRoute) {
    return NextResponse.redirect(new URL(DEFAULT_PROTECTED, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
