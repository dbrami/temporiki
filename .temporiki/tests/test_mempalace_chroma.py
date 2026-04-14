from __future__ import annotations

from temporiki_tools.mempalace_chroma import is_chroma_available


def test_is_chroma_available_returns_false_when_client_init_raises(monkeypatch) -> None:
    def _boom():
        raise RuntimeError("client init failed")

    monkeypatch.setattr("temporiki_tools.mempalace_chroma._client", _boom)
    assert is_chroma_available() is False


def test_is_chroma_available_returns_false_when_heartbeat_raises(monkeypatch) -> None:
    class _Client:
        def heartbeat(self) -> None:
            raise RuntimeError("heartbeat failed")

    monkeypatch.setattr("temporiki_tools.mempalace_chroma._client", lambda: _Client())
    assert is_chroma_available() is False
