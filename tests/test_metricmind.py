from pathlib import Path

from src.semantic_engine import MetricMindEngine


ROOT = Path(__file__).parents[1]


def make_engine():
    return MetricMindEngine(ROOT / "data" / "sales.csv", ROOT / "semantic_layer" / "metrics.yml")


def test_revenue_query_is_deterministic():
    engine = make_engine()
    first = engine.execute("Show Q3 2025 revenue")
    second = engine.execute("Show Q3 2025 revenue")
    assert first["value"] == second["value"]
    assert first["payload"]["governed"] is True


def test_european_breakdown_uses_region_filter():
    engine = make_engine()
    result = engine.execute("Show European sales by country")
    assert result["parsed"]["region"] == "Europe"
    assert result["parsed"]["group_by"] == "country"
    assert len(result["data"]) == 4


def test_margin_metric_is_between_zero_and_one():
    engine = make_engine()
    result = engine.execute("Show Q4 2025 margin")
    assert 0 < result["value"] < 1
