from game.state import Zone, Season


SEASONAL_MODIFIERS: dict[Season, dict[str, float]] = {
    Season.SPRING: {"food": 1.15, "medicine": 1.20, "wood": 1.0, "stone": 1.0, "hides": 0.9},
    Season.SUMMER: {"food": 1.10, "medicine": 1.30, "wood": 1.0, "stone": 1.0, "hides": 1.0},
    Season.AUTUMN: {"food": 1.05, "medicine": 0.90, "wood": 1.10, "stone": 1.0, "hides": 1.15},
    Season.WINTER: {"food": 0.80, "medicine": 0.70, "wood": 0.90, "stone": 1.0, "hides": 1.20},
}

BASE_REGENERATION: dict[str, float] = {
    "food": 5.0,
    "medicine": 2.0,
    "wood": 3.0,
    "stone": 1.0,
    "hides": 1.0,
}

RESOURCE_CAPS: dict[str, float] = {
    "food": 100.0,
    "medicine": 60.0,
    "wood": 80.0,
    "stone": 50.0,
    "hides": 40.0,
}


def apply_seasonal_tick(zones: list[Zone], season: Season) -> list[Zone]:
    modifiers = SEASONAL_MODIFIERS[season]
    updated = []
    for zone in zones:
        new_resources = dict(zone.resources)
        for resource, base_regen in BASE_REGENERATION.items():
            seasonal_regen = base_regen * modifiers.get(resource, 1.0)
            current = new_resources.get(resource, 0.0)
            cap = RESOURCE_CAPS.get(resource, 100.0)
            new_resources[resource] = min(cap, current + seasonal_regen)
        updated.append(zone.model_copy(update={"resources": new_resources}))
    return updated
