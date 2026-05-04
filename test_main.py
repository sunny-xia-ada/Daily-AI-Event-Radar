import pytest
from main import Event, deduplicate_events, score_event_fallback

def test_normalize_string():
    e = Event("  Hello   World!  ", "2026-06-01", "Seattle", "Organizer", "http", "desc", "test")
    assert e.normalized_title == "hello world"

def test_deduplication():
    e1 = Event("AI Hackathon!", "2026-06-01", "Seattle", "Org", "http://1", "Desc1", "luma")
    e2 = Event("ai hackathon", "2026-06-01", "Seattle, WA", "Org", "http://2", "Longer Description Here", "meetup")
    
    unique = deduplicate_events([e1, e2])
    assert len(unique) == 1
    merged = unique[0]
    assert "luma" in merged.sources
    assert "meetup" in merged.sources
    assert merged.description == "Longer Description Here"
    assert merged.location == "Seattle, WA"

def test_score_fallback():
    e_good = Event("Agent Hackathon", "2026-06-01", "Seattle", "Org", "http", "desc", "test")
    score_event_fallback(e_good)
    assert e_good.relevance_score >= 7
    assert e_good.recommendation == "Best Matches"

    e_bad = Event("Business Marketing 101", "2026-06-01", "Online", "Org", "http", "beginner tutorial", "test")
    score_event_fallback(e_bad)
    assert e_bad.relevance_score < 4
    assert e_bad.recommendation == "Low Priority / Skip"

def test_source_error_handling(monkeypatch):
    from main import fetch_from_tavily
    # Assuming the API key is not set, it should raise ValueError
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    with pytest.raises(ValueError, match="TAVILY_API_KEY missing"):
        fetch_from_tavily()
