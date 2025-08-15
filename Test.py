#Creates a json file with volume. this file then goes into Volume_jsonConverter

import json
import requests
from time import sleep
from tqdm import tqdm
from datetime import datetime

INPUT_FILE = "open_markets_wip.json"
OUTPUT_FILE_TEMPLATE = "open_markets_wip_with_volume_{}.json"
GAMMA_API_URL = "https://gamma-api.polymarket.com/markets"
REQUEST_DELAY = 0.2  # seconds

def fetch_gamma_markets():
    """Fetch all markets from Gamma API."""
    response = requests.get(GAMMA_API_URL)
    response.raise_for_status()
    return response.json()

def map_conditionid_to_volume(gamma_markets):
    """Return a mapping from conditionId to volume."""
    condition_volume_map = {}
    for market in gamma_markets:
        condition_id = market.get("conditionId")
        volume = market.get("volumeNum") or market.get("volume")
        if condition_id:
            condition_volume_map[condition_id] = volume
    return condition_volume_map

def main():
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    # Support both list and dict structure
    if isinstance(data, dict):
        markets = data.get("markets", [])
    elif isinstance(data, list):
        markets = data
    else:
        raise ValueError("Invalid JSON format: expected dict or list.")

    print(f"📥 Loaded {len(markets)} markets from {INPUT_FILE}")

    try:
        gamma_data = fetch_gamma_markets()
        condition_volume_map = map_conditionid_to_volume(gamma_data)
        print(f"📊 Loaded volume data for {len(condition_volume_map)} condition IDs")
    except Exception as e:
        print(f"❌ Failed to fetch market volumes: {e}")
        condition_volume_map = {}

    # Update each market with volume using conditionId
    for market in tqdm(markets):
        condition_id = market.get("conditionId")
        volume = condition_volume_map.get(condition_id)
        market["volume"] = volume if volume is not None else None

    # Save to output
    timestamp = datetime.utcnow().isoformat()
    output_file = OUTPUT_FILE_TEMPLATE.format(timestamp.split("T")[0])
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "markets": markets
        }, f, indent=2)

    print(f"✅ Saved updated market data to {output_file}")

if __name__ == "__main__":
    main()
