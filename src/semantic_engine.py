from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

REGION_ALIASES = {
    "europe": "Europe",
    "european": "Europe",
    "asia": "Asia-Pacific",
    "apac": "Asia-Pacific",
    "north america": "North America",
    "america": "North America",
}


class MetricMindEngine:
    """Small governed semantic query engine for the Month 1 prototype."""

    def __init__(self, data_path: str | Path, metrics_path: str | Path):
        self.data_path = Path(data_path)
        self.metrics_path = Path(metrics_path)
        self.data = pd.read_csv(self.data_path, parse_dates=["date"])
        self.data["year"] = self.data["date"].dt.year
        self.data["quarter"] = "Q" + self.data["date"].dt.quarter.astype(str)
        self.semantic_spec = yaml.safe_load(self.metrics_path.read_text(encoding="utf-8"))

    def parse_question(self, question: str) -> dict[str, Any]:
        text = question.lower().strip()
        intent = "summary"
        if "why" in text or "drop" in text or "decrease" in text or "decline" in text:
            intent = "root_cause"
        elif "compare" in text or "by region" in text or "by country" in text or "breakdown" in text:
            intent = "breakdown"

        metric = "revenue"
        for candidate in ["margin", "profit", "cost", "revenue"]:
            if candidate in text:
                metric = candidate
                break

        quarter_match = re.search(r"\bq([1-4])\b", text)
        year_match = re.search(r"\b(20\d{2})\b", text)
        region = None
        for alias, canonical in REGION_ALIASES.items():
            if alias in text:
                region = canonical
                break
        group_by = None
        if "country" in text:
            group_by = "country"
        elif "region" in text:
            group_by = "region"
        elif "product" in text:
            group_by = "product"

        return {
            "intent": intent,
            "metric": metric,
            "quarter": f"Q{quarter_match.group(1)}" if quarter_match else None,
            "year": int(year_match.group(1)) if year_match else None,
            "region": region,
            "group_by": group_by,
        }

    def compile_payload(self, question: str, parsed: dict[str, Any]) -> dict[str, Any]:
        filters = {}
        if parsed.get("year"):
            filters["year"] = parsed["year"]
        if parsed.get("quarter"):
            filters["quarter"] = parsed["quarter"]
        if parsed.get("region"):
            filters["region"] = parsed["region"]
        return {
            "metric": parsed["metric"],
            "dimensions": [parsed["group_by"]] if parsed.get("group_by") else [],
            "filters": filters,
            "limit": int(self.semantic_spec.get("max_rows", 1000)),
            "governed": True,
            "source": "metricmind.semantic_layer",
        }

    def _filter_data(self, parsed: dict[str, Any]) -> pd.DataFrame:
        result = self.data.copy()
        for column in ["year", "quarter", "region"]:
            value = parsed.get(column)
            if value is not None:
                result = result[result[column] == value]
        return result

    @staticmethod
    def _metric_value(frame: pd.DataFrame, metric: str) -> float:
        revenue = frame["revenue"].sum()
        cost = frame["cost"].sum()
        if metric == "revenue":
            return float(revenue)
        if metric == "cost":
            return float(cost)
        if metric == "profit":
            return float(revenue - cost)
        if metric == "margin":
            return float((revenue - cost) / revenue) if revenue else 0.0
        raise ValueError(f"Metric not permitted: {metric}")

    def execute(self, question: str) -> dict[str, Any]:
        parsed = self.parse_question(question)
        payload = self.compile_payload(question, parsed)
        frame = self._filter_data(parsed)
        metric = parsed["metric"]

        if parsed["intent"] == "root_cause":
            current = frame
            if parsed.get("quarter") == "Q1":
                previous = self._filter_data({**parsed, "quarter": "Q4", "year": (parsed.get("year") or 2025) - 1})
            else:
                previous_q = {"Q2": "Q1", "Q3": "Q2", "Q4": "Q3"}.get(parsed.get("quarter"), "Q1")
                previous = self._filter_data({**parsed, "quarter": previous_q})
            current_cost = current.groupby("cost_driver", as_index=False)["cost"].sum()
            previous_cost = previous.groupby("cost_driver", as_index=False)["cost"].sum()
            cause = current_cost.merge(previous_cost, on="cost_driver", how="outer", suffixes=("_current", "_previous")).fillna(0)
            cause["change"] = cause["cost_current"] - cause["cost_previous"]
            cause = cause.sort_values("change", ascending=False)
            return {
                "question": question,
                "parsed": parsed,
                "payload": payload,
                "headline": f"{parsed.get('region') or 'Overall'} {metric} root-cause analysis",
                "value": self._metric_value(frame, metric),
                "data": cause.to_dict("records"),
                "chart_type": "bar",
            }

        if parsed.get("group_by"):
            grouped = frame.groupby(parsed["group_by"], as_index=False).agg(
                revenue=("revenue", "sum"),
                cost=("cost", "sum"),
            )
            grouped["profit"] = grouped["revenue"] - grouped["cost"]
            grouped["margin"] = grouped["profit"] / grouped["revenue"]
            output = grouped[[parsed["group_by"], metric]].sort_values(metric, ascending=False)
            records = output.to_dict("records")
            chart_type = "bar"
        else:
            records = [{"metric": metric, "value": self._metric_value(frame, metric)}]
            chart_type = "kpi"

        return {
            "question": question,
            "parsed": parsed,
            "payload": payload,
            "headline": f"{metric.title()} analysis",
            "value": self._metric_value(frame, metric),
            "data": records,
            "chart_type": chart_type,
        }
