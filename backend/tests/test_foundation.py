"""Backend foundation tests for VGC Intelligence."""
import os
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "https://vgc-intelligence.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

EMPTY_LIST_ENDPOINTS = [
    "/v1/pokemon", "/v1/moves", "/v1/items", "/v1/abilities",
    "/v1/teams", "/v1/tournaments", "/v1/standings",
    "/v1/meta/usage", "/v1/cores",
]

ADAPTERS = {"pikalytics", "munchstats", "replica_teams", "labmaus",
            "reportworm", "cut_explorer", "showdown", "vgc_guide"}


def test_api_root():
    r = requests.get(API, timeout=15)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j.get("service")
    assert "v1" in j.get("versions", [])


def test_health():
    r = requests.get(f"{API}/v1/health", timeout=15)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_health_db():
    r = requests.get(f"{API}/v1/health/db", timeout=20)
    assert r.status_code == 200, r.text


@pytest.mark.parametrize("path", EMPTY_LIST_ENDPOINTS)
def test_empty_list_endpoints(path):
    r = requests.get(f"{API}{path}", timeout=15)
    assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
    j = r.json()
    assert isinstance(j, list), f"{path} did not return a list"
    assert j == [], f"{path} expected empty list, got {j[:2]}"


def test_sources_registry():
    r = requests.get(f"{API}/v1/sources", timeout=15)
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j, list)
    keys = {a.get("key") for a in j}
    assert ADAPTERS.issubset(keys), f"Missing adapters: {ADAPTERS - keys}"
    for a in j:
        if a.get("key") in ADAPTERS:
            assert a.get("implemented") is False, f"{a['key']} should be implemented=false"
