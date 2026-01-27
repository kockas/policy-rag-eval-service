from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from io import BytesIO
from pathlib import PurePosixPath
import os
import re
import time
from typing import Iterable, List, Set
from urllib.parse import urljoin, urlparse

import httpx
from pypdf import PdfReader

from policy_rag_eval.retrieval.types import Document


_DEFAULT_SEEDS = [
    "https://www.finma.ch/en/documentation/",
    "https://www.finma.ch/en/documentation/circulars/",
    "https://www.finma.ch/en/documentation/finma-guidance/",
]


@dataclass(frozen=True)
class _FetchedDoc:
    url: str
    text: str


@dataclass(frozen=True)
class FinmaSearchResult:
    doc_id: str
    title: str
    description: str
    url: str
    date: str | None
    doc_type: str | None
    category: str | None


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _seed_urls() -> list[str]:
    raw = os.getenv("FINMA_SEED_URLS")
    if not raw:
        return list(_DEFAULT_SEEDS)
    return [u.strip() for u in raw.split(",") if u.strip()]


def _allowed(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.endswith("finma.ch") and parsed.scheme in {"http", "https"}


def _extract_links(html: str, base_url: str) -> list[str]:
    links = []
    for match in re.findall(r"href=[\"']([^\"']+)[\"']", html, flags=re.IGNORECASE):
        href = unescape(match).strip()
        if href.startswith("#"):
            continue
        full = urljoin(base_url, href)
        if _allowed(full):
            links.append(full)
    return links


def _html_to_text(html: str) -> str:
    # Drop script/style blocks to reduce noise.
    cleaned = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    cleaned = re.sub(r"<style[\s\S]*?</style>", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return unescape(cleaned).strip()


def _pdf_to_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _doc_id_from_url(url: str) -> str:
    path = PurePosixPath(urlparse(url).path)
    name = path.stem or "document"
    return re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-")


def _finma_search_endpoint() -> str:
    return os.getenv("FINMA_SEARCH_URL", "https://www.finma.ch/en/api/search/getresult")


def _finma_search_source() -> str:
    return os.getenv("FINMA_SEARCH_SOURCE_ID", "{15F93962-20ED-419C-AC2C-1FF035FE4A31}")


def _finma_search_order() -> str:
    return os.getenv("FINMA_SEARCH_ORDER", "4")


def _normalize_search_url(link: str) -> str:
    if not link:
        return ""
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return urljoin("https://www.finma.ch", link)


def _parse_search_item(item: dict) -> FinmaSearchResult | None:
    link = _normalize_search_url(item.get("Link", ""))
    if not link:
        return None
    raw_id = item.get("Id")
    doc_id = (
        _doc_id_from_url(link)
        if not raw_id
        else re.sub(r"[^A-Za-z0-9_-]+", "-", str(raw_id)).strip("-")
    )
    title = (item.get("Title") or "").strip()
    description = (item.get("Description") or "").strip()
    return FinmaSearchResult(
        doc_id=doc_id or "document",
        title=title,
        description=description,
        url=link,
        date=item.get("Date"),
        doc_type=item.get("Type"),
        category=item.get("Category"),
    )


def search_finma(query: str, top_k: int) -> list[FinmaSearchResult]:
    if not query:
        return []

    endpoint = _finma_search_endpoint()
    payload = {
        "query": query,
        "Order": _finma_search_order(),
        "ds": _finma_search_source(),
    }
    headers = {"User-Agent": "policy-rag-eval-service/0.1"}
    timeout = _env_float("FINMA_TIMEOUT", 10.0)
    results: list[FinmaSearchResult] = []
    next_link = endpoint

    with httpx.Client(timeout=timeout, headers=headers) as client:
        while next_link and len(results) < top_k:
            if next_link == endpoint:
                resp = client.post(next_link, data=payload)
            else:
                resp = client.post(_normalize_search_url(next_link), data=payload)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("Items", []):
                parsed = _parse_search_item(item)
                if parsed:
                    results.append(parsed)
                    if len(results) >= top_k:
                        break
            next_link = data.get("NextPageLink")

    return results


def _fetch_url(client: httpx.Client, url: str, max_bytes: int) -> _FetchedDoc | None:
    resp = client.get(url)
    resp.raise_for_status()
    content_type = resp.headers.get("content-type", "")
    if "pdf" in content_type or url.lower().endswith(".pdf"):
        if len(resp.content) > max_bytes:
            return None
        text = _pdf_to_text(resp.content)
        return _FetchedDoc(url=url, text=text)

    if "text/html" in content_type or "html" in content_type:
        text = _html_to_text(resp.text)
        return _FetchedDoc(url=url, text=text)

    return None


def _crawl(seed_urls: Iterable[str]) -> list[str]:
    max_pages = _env_int("FINMA_MAX_PAGES", 30)
    max_depth = _env_int("FINMA_MAX_DEPTH", 1)

    visited: Set[str] = set()
    frontier = list(seed_urls)
    depth = 0

    all_links: list[str] = []

    headers = {"User-Agent": "policy-rag-eval-service/0.1"}
    with httpx.Client(timeout=_env_float("FINMA_TIMEOUT", 10.0), headers=headers) as client:
        while frontier and depth <= max_depth and len(visited) < max_pages:
            next_frontier: list[str] = []
            for url in frontier:
                if url in visited or len(visited) >= max_pages:
                    continue
                visited.add(url)
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                if "text/html" not in resp.headers.get("content-type", ""):
                    continue

                links = _extract_links(resp.text, url)
                all_links.extend(links)
                for link in links:
                    if link not in visited and _allowed(link):
                        next_frontier.append(link)
            frontier = next_frontier
            depth += 1

    return list(dict.fromkeys(all_links))


def load_finma_documents() -> List[Document]:
    max_docs = _env_int("FINMA_MAX_DOCS", 10)
    max_bytes = _env_int("FINMA_MAX_PDF_BYTES", 8_000_000)

    seed_urls = _seed_urls()
    urls = _crawl(seed_urls)

    # Prefer PDFs, but keep a few HTML pages as fallback.
    pdf_urls = [u for u in urls if u.lower().endswith(".pdf")]
    html_urls = [u for u in urls if u.lower().endswith(".pdf") is False]

    chosen = pdf_urls[:max_docs] if pdf_urls else html_urls[:max_docs]

    documents: List[Document] = []
    headers = {"User-Agent": "policy-rag-eval-service/0.1"}
    with httpx.Client(timeout=_env_float("FINMA_TIMEOUT", 10.0), headers=headers) as client:
        for url in chosen:
            try:
                fetched = _fetch_url(client, url, max_bytes=max_bytes)
            except httpx.HTTPError:
                continue
            if not fetched or not fetched.text:
                continue
            doc_id = _doc_id_from_url(url)
            documents.append(Document(doc_id=doc_id, source=url, text=fetched.text))

    return documents
