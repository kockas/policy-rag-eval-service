import pytest

from policy_rag_eval.retrieval.finma import FinmaSearchResult, search_finma


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, responses: list[_FakeResponse]):
        self._responses = responses
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, data):
        self.calls.append((url, data))
        if not self._responses:
            raise AssertionError("No more fake responses available.")
        return self._responses.pop(0)


def _make_item(link: str, title: str = "Title", description: str = "Desc", raw_id: str | None = None):
    item = {
        "Title": title,
        "Description": description,
        "Link": link,
        "Type": "News",
        "Category": "Category",
        "Date": "27 January 2026",
    }
    if raw_id is not None:
        item["Id"] = raw_id
    return item


def test_search_finma_paginates_and_limits(monkeypatch: pytest.MonkeyPatch):
    page1 = _FakeResponse(
        {
            "Items": [
                _make_item("/en/news/2026/01/example-1/"),
                _make_item("https://www.finma.ch/en/news/2026/01/example-2/"),
            ],
            "NextPageLink": "/api/search/getresult?Skip=25",
        }
    )
    page2 = _FakeResponse(
        {
            "Items": [
                _make_item("/en/news/2026/01/example-3/"),
            ],
            "NextPageLink": None,
        }
    )

    fake_client = _FakeClient([page1, page2])

    monkeypatch.setattr("policy_rag_eval.retrieval.finma.httpx.Client", lambda **_: fake_client)

    results = search_finma("bank", top_k=3)
    assert len(results) == 3
    assert all(isinstance(r, FinmaSearchResult) for r in results)
    assert fake_client.calls[0][0] == "https://www.finma.ch/en/api/search/getresult"
    assert fake_client.calls[1][0] == "https://www.finma.ch/api/search/getresult?Skip=25"


def test_search_finma_short_circuits_on_top_k(monkeypatch: pytest.MonkeyPatch):
    page1 = _FakeResponse(
        {
            "Items": [
                _make_item("/en/news/2026/01/example-1/"),
                _make_item("/en/news/2026/01/example-2/"),
            ],
            "NextPageLink": "/api/search/getresult?Skip=25",
        }
    )
    page2 = _FakeResponse(
        {
            "Items": [
                _make_item("/en/news/2026/01/example-3/"),
            ],
            "NextPageLink": None,
        }
    )
    fake_client = _FakeClient([page1, page2])
    monkeypatch.setattr("policy_rag_eval.retrieval.finma.httpx.Client", lambda **_: fake_client)

    results = search_finma("bank", top_k=2)
    assert len(results) == 2
    assert len(fake_client.calls) == 1


def test_search_finma_empty_query(monkeypatch: pytest.MonkeyPatch):
    fake_client = _FakeClient([])
    monkeypatch.setattr("policy_rag_eval.retrieval.finma.httpx.Client", lambda **_: fake_client)

    results = search_finma("", top_k=5)
    assert results == []
    assert fake_client.calls == []
