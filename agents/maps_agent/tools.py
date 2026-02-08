"""
Tools for the Maps Agent — provides directions and map links via Google Maps API.
"""

import os
import googlemaps
from urllib.parse import quote_plus


def get_directions(origin: str, destination: str, mode: str = "driving") -> dict:
    """Get step-by-step directions between two locations.

    Args:
        origin: Starting location (address or place name).
        destination: Ending location (address or place name).
        mode: Travel mode — driving, walking, bicycling, or transit. Defaults to driving.

    Returns:
        A dict with route summary, steps, duration, and distance.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"status": "error", "detail": "GOOGLE_MAPS_API_KEY is not configured."}

    try:
        gmaps = googlemaps.Client(key=api_key)
        result = gmaps.directions(origin, destination, mode=mode)

        if not result:
            return {
                "status": "error",
                "detail": f"No route found from '{origin}' to '{destination}'.",
            }

        route = result[0]
        leg = route["legs"][0]

        steps = []
        for step in leg["steps"]:
            # Strip HTML tags from instructions
            instruction = step["html_instructions"]
            import re
            instruction = re.sub(r"<[^>]+>", " ", instruction).strip()
            instruction = re.sub(r"\s+", " ", instruction)
            steps.append({
                "instruction": instruction,
                "distance": step["distance"]["text"],
                "duration": step["duration"]["text"],
            })

        map_link = get_map_link(origin, destination, mode)

        return {
            "status": "success",
            "origin": leg["start_address"],
            "destination": leg["end_address"],
            "distance": leg["distance"]["text"],
            "duration": leg["duration"]["text"],
            "mode": mode,
            "steps": steps,
            "map_url": map_link["url"],
        }
    except googlemaps.exceptions.ApiError as e:
        return {"status": "error", "detail": f"Google Maps API error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "detail": f"Failed to get directions: {str(e)}"}


def get_map_link(origin: str, destination: str, mode: str = "driving") -> dict:
    """Generate a Google Maps URL with directions between two locations.

    Args:
        origin: Starting location (address or place name).
        destination: Ending location (address or place name).
        mode: Travel mode — driving, walking, bicycling, or transit. Defaults to driving.

    Returns:
        A dict with the Google Maps directions URL.
    """
    base_url = "https://www.google.com/maps/dir/"
    origin_encoded = quote_plus(origin)
    destination_encoded = quote_plus(destination)
    url = f"{base_url}?api=1&origin={origin_encoded}&destination={destination_encoded}&travelmode={mode}"

    return {
        "status": "success",
        "url": url,
        "detail": f"Google Maps link for directions from '{origin}' to '{destination}' by {mode}.",
    }
