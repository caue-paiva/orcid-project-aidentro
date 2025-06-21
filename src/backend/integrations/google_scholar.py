from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from pygscholar import api as gscholar

try:
    from fp.fp import FreeProxy
except ImportError:
    FreeProxy = None


@dataclass(slots=True)
class CitationData:
    year: int
    citations: int
    cumulative_citations: int = 0


@dataclass(slots=True)
class AuthorMetrics:
    name: str
    scholar_id: Optional[str]
    total_citations: int
    h_index: int
    i10_index: int
    citations_per_year: Dict[int, int]
    publications_count: int


def _collect_proxies(max_proxies: int = 15) -> List[str]:
    proxies: list[str] = []
    if FreeProxy is None:
        return proxies

    fp = FreeProxy(rand=True, timeout=1, anonym=True)
    for _ in range(max_proxies):
        try:
            ip_port = fp.get()
            if ip_port:
                proxies.append(f"http://{ip_port}")
        except Exception:
            break
    return proxies


class GoogleScholarAPI:
    def __init__(self, delay: float = 1.0, use_proxy: bool = True) -> None:
        self.delay = max(delay, 0.0)
        self._proxies: List[Optional[str]] = _collect_proxies() if use_proxy else []
        self._proxies.append(None)
        self._idx = 0

    def _set_proxy_env(self, proxy: Optional[str]) -> None:
        if proxy:
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
        else:
            os.environ.pop("HTTP_PROXY", None)
            os.environ.pop("HTTPS_PROXY", None)

    def _run_rotating(self, fn, *args, **kw):
        tried, total = 0, len(self._proxies)
        while tried < total:
            proxy = self._proxies[self._idx]
            self._set_proxy_env(proxy)
            try:
                return fn(*args, **kw)
            except Exception as exc:
                if proxy is not None:
                    print(f"Proxy {proxy} failed: {exc}")
                    self._proxies.pop(self._idx)
                    total -= 1
                    if total == 0:
                        raise
                    self._idx %= total
                else:
                    raise
            tried += 1
        raise RuntimeError("All proxies failed")

    def search_author(self, name: str, aff: str | None = None, idx: int = 0):
        def core():
            authors = gscholar.search_author(name)
            if not authors:
                return None
            if aff:
                authors = [a for a in authors if aff.lower() in str(a.affiliation).lower()] or authors
            return self._fmt_author(authors[idx])

        try:
            return self._run_rotating(core)
        except Exception as e:
            print(f"Error searching author: {e}")
            return None

    def get_author_by_id(self, scholar_id: str):
        try:
            return self._run_rotating(lambda: self._fmt_author(gscholar.get_author(scholar_id)))
        except Exception as e:
            print(f"Error fetching author {scholar_id}: {e}")
            return None

    def get_author_metrics(self, name: str, aff: str | None = None):
        data = self.search_author(name, aff)
        if data is None:
            return None
        return AuthorMetrics(
            name=data["name"] or name,
            scholar_id=data["scholar_id"],
            total_citations=data["total_citations"],
            h_index=data["h_index"],
            i10_index=data["i10_index"],
            citations_per_year=data["citations_per_year"],
            publications_count=len(data.get("publications", [])),
        )

    def get_citations_by_year(self, n: str, y: int, aff: str | None = None):
        d = self.search_author(n, aff)
        return None if d is None else d["citations_per_year"].get(y, 0)

    def get_citations_for_years(self, n: str, yrs: Sequence[int], aff: str | None = None):
        d = self.search_author(n, aff) or {}
        per_year = d.get("citations_per_year", {})
        return {y: per_year.get(y, 0) for y in yrs}

    def get_cumulative_citations(self, n: str, yrs: Sequence[int], aff: str | None = None):
        yrs = sorted(set(yrs))
        yearly = self.get_citations_for_years(n, yrs, aff)
        tot = 0
        return [
            CitationData(y, yearly.get(y, 0), (tot := tot + yearly.get(y, 0)))
            for y in yrs
        ]

    def search_publications(self, n: str, limit: int = 20):
        a = self.search_author(n)
        if a is None:
            return []
        pubs = a.get("publications", [])[:limit]
        out = []
        for i, p in enumerate(pubs):
            if i:
                time.sleep(self.delay)
            out.append(self._fmt_pub(p))
        return out

    @staticmethod
    def _fmt_author(a):
        return {
            "name": getattr(a, "name", "-"),
            "scholar_id": getattr(a, "scholar_id", None),
            "affiliation": getattr(a, "affiliation", ""),
            "email": getattr(a, "email", ""),
            "total_citations": getattr(a, "citedby", 0),
            "h_index": getattr(a, "h_index", getattr(a, "hindex", 0)),
            "i10_index": getattr(a, "i10_index", getattr(a, "i10index", 0)),
            "citations_per_year": getattr(a, "cites_per_year", {}) or {},
            "publications": getattr(a, "publications", []) or [],
            "interests": getattr(a, "interests", []) or [],
        }

    @staticmethod
    def _fmt_pub(p):
        bib = getattr(p, "bib", {})
        return {
            "title": bib.get("title", ""),
            "authors": bib.get("author", ""),
            "venue": bib.get("venue", ""),
            "year": bib.get("pub_year"),
            "citations": getattr(p, "num_citations", 0),
            "url": getattr(p, "pub_url", ""),
            "abstract": bib.get("abstract", ""),
        }


def _api():
    if not hasattr(_api, "_inst"):
        _api._inst = GoogleScholarAPI()
    return _api._inst


def get_author_citations_by_year(name, year, aff=None):
    return _api().get_citations_by_year(name, year, aff)


def get_author_citations_for_years(name, years, aff=None):
    return _api().get_citations_for_years(name, years, aff)


def get_cumulative_citations(name, years, aff=None):
    return _api().get_cumulative_citations(name, years, aff)


def get_complete_author_metrics(name, aff=None):
    return _api().get_author_metrics(name, aff)