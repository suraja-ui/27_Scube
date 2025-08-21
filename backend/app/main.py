from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests, re
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Website Audit Tool")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditIn(BaseModel):
    url: HttpUrl

SEC_HEADERS = [
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "strict-transport-security",
]

def safe_get(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent":"AuditBot/1.0"})
        return r
    except Exception:
        return None

def get_base_url(url):
    m = re.match(r'^(https?://[^/]+)', str(url))
    return m.group(1) if m else str(url)

def kb(n):
    return round(n/1024, 1)

@app.post("/audit")
def audit(payload: AuditIn):
    url = str(payload.url).strip()
    r = safe_get(url)
    if r is None:
        raise HTTPException(400, "Unable to fetch URL")
    content = r.content or b""
    size_bytes = len(content)
    text = r.text or ""
    soup = BeautifulSoup(text, "html.parser")


    issues, passes = [], []
    scores = {"security": 0, "seo": 0, "performance": 0, "accessibility": 0}

    if url.startswith("https://"):
        passes.append("Uses HTTPS"); scores["security"] += 25
        if "strict-transport-security" in (h.lower() for h in r.headers.keys()):
            passes.append("HSTS enabled"); scores["security"] += 10
    else:
        issues.append("Site is not using HTTPS (use TLS)")

    present, missing = [], []
    for h in SEC_HEADERS:
        if h in (k.lower() for k in r.headers.keys()):
            present.append(h)
        else:
            missing.append(h)
    if present: passes.append(f"Security headers present: {', '.join(present)}"); scores["security"] += min(40, 10*len(present))
    if missing: issues.append(f"Missing headers: {', '.join(missing)}")

    if url.startswith("https://"):
        insecure_links = [tag.get("src") or tag.get("href") for tag in soup.find_all(src=True)+soup.find_all(href=True) if (tag.get("src") or tag.get("href")).startswith("http://")]
        if insecure_links: issues.append(f"Mixed content: {len(insecure_links)} http:// resources found")
        else: passes.append("No mixed content found"); scores["security"] += 25

    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    if title and 10 <= len(title) <= 60: passes.append("SEO: Title present with good length"); scores["seo"] += 25
    else: issues.append("SEO: Missing or poor title (10–60 chars recommended)")

    meta_desc = soup.find("meta", attrs={"name":"description"})
    desc = meta_desc.get("content", "").strip() if meta_desc else ""
    if desc and 50 <= len(desc) <= 160: passes.append("SEO: Meta description present with good length"); scores["seo"] += 25
    else: issues.append("SEO: Add a meta description (50–160 chars)")

    h1 = soup.find_all("h1")
    if len(h1) == 1: passes.append("SEO: Single H1 present"); scores["seo"] += 15
    elif len(h1) == 0: issues.append("SEO: No H1 found (add one main heading)")
    else: issues.append("SEO: Multiple H1s found (keep exactly one)")

    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"): passes.append("SEO: Canonical link present"); scores["seo"] += 10

    base_url = get_base_url(url)
    robots = safe_get(base_url + "/robots.txt")
    if robots and robots.status_code == 200: passes.append("SEO: robots.txt found"); scores["seo"] += 10
    else: issues.append("SEO: robots.txt not found")

    if size_bytes <= 2_000_000: passes.append(f"Page size OK: {kb(size_bytes)} KB"); scores["performance"] += 25
    else: issues.append(f"Large page: {kb(size_bytes)} KB (optimize images/assets)")

    cache_headers = ["cache-control","etag","last-modified"]
    if any(h in (k.lower() for k in r.headers.keys()) for h in cache_headers): passes.append("Uses caching headers"); scores["performance"] += 20
    else: issues.append("No caching headers (add Cache-Control/ETag/Last-Modified)")

    resources = soup.find_all(["img","script","link"])
    if len(resources) <= 100: passes.append("Reasonable number of resources"); scores["performance"] += 15
    else: issues.append(f"Heavy page: {len(resources)} resources (reduce requests)")

    imgs = soup.find_all("img")
    no_dims = [i for i in imgs if not i.get("width") or not i.get("height")]
    if len(no_dims) == 0: passes.append("Images set width/height (better CLS)"); scores["performance"] += 10
    else: issues.append(f"{len(no_dims)} images missing width/height")

    enc = r.headers.get("content-encoding","").lower()
    if "gzip" in enc or "br" in enc or "zstd" in enc: passes.append("Response compressed"); scores["performance"] += 15
    else: issues.append("No compression (enable gzip/br)")

    missing_alt = [i for i in imgs if not i.get("alt")]
    if len(missing_alt) == 0: passes.append("All images have alt text"); scores["accessibility"] += 40
    else: issues.append(f"{len(missing_alt)} images missing alt text")

    for k in scores: scores[k] = max(0, min(100, scores[k]))
    recommendations = issues[:5]

    return {
        "url": url, "status_code": r.status_code, "scores": scores,
        "summary": {"passes": passes[:10], "issues": issues[:15], "recommendations": recommendations},
        "page": {"title": title, "description_len": len(desc), "size_bytes": size_bytes, "resource_count": len(resources)}
    }
