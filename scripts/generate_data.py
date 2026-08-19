from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm


def main() -> None:
    rng = np.random.default_rng(42)
    rows = []
    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    regions = {
        "Europe": ["Germany", "France", "United Kingdom", "Spain"],
        "North America": ["United States", "Canada", "Mexico"],
        "Asia-Pacific": ["India", "Japan", "Australia", "Singapore"],
    }
    products = ["Analytics Suite", "Cloud Platform", "Security Module"]
    channels = ["Direct", "Partner", "Online"]
    for date_value in tqdm(dates, desc="Generating synthetic sales data"):
        for region, countries in regions.items():
            for country in countries:
                for product in products:
                    revenue = float(rng.normal(18500, 2800))
                    material = revenue * rng.uniform(0.34, 0.44)
                    shipping = revenue * rng.uniform(0.04, 0.10)
                    labor = revenue * rng.uniform(0.10, 0.16)
                    rows.append(
                        {
                            "date": date_value,
                            "region": region,
                            "country": country,
                            "product": product,
                            "channel": rng.choice(channels),
                            "revenue": round(max(revenue, 1000), 2),
                            "cost": round(max(material + shipping + labor, 500), 2),
                            "cost_driver": rng.choice(["Material", "Shipping", "Labor"], p=[0.55, 0.25, 0.20]),
                        }
                    )
    frame = pd.DataFrame(rows)
    output = Path(__file__).parents[1] / "data" / "sales.csv"
    output.parent.mkdir(exist_ok=True)
    frame.to_csv(output, index=False)
    print(f"Saved {len(frame):,} rows to {output}")


if __name__ == "__main__":
    main()
