import pytest


@pytest.fixture
def no_network(monkeypatch):
    """Marker fixture reserved for tests that must never access the network."""
    return monkeypatch


@pytest.fixture(autouse=True)
def disable_pipeline_metadata_side_effects(monkeypatch):
    """Keep pipeline unit tests independent from the local FFmpeg install."""
    monkeypatch.setattr(
        "audiobook_generator.core.pipeline.tag_mp3",
        lambda *args, **kwargs: True,
    )
