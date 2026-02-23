import { defineMiddleware } from "astro:middleware";

function shouldRedirectToTrailingSlash(pathname: string): boolean {
  if (!pathname.startsWith("/blog")) {
    return false;
  }

  if (pathname === "/blog") {
    return true;
  }

  if (pathname.endsWith("/")) {
    return false;
  }

  const lastSegment = pathname.slice(pathname.lastIndexOf("/") + 1);
  if (!lastSegment) {
    return false;
  }

  // Keep file-like paths unchanged, e.g. /blog/rss.xml
  if (lastSegment.includes(".")) {
    return false;
  }

  return true;
}

export const onRequest = defineMiddleware(async (context, next) => {
  const method = context.request.method.toUpperCase();
  if (method !== "GET" && method !== "HEAD") {
    return next();
  }

  const url = new URL(context.request.url);
  if (!shouldRedirectToTrailingSlash(url.pathname)) {
    return next();
  }

  url.pathname = `${url.pathname}/`;
  return Response.redirect(url, 301);
});
