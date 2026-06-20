import random
import uuid
from typing import Optional
from game.state import SharedFiction, Character, FictionDelta


def apply_belief_tick(
    fictions: list[SharedFiction], characters: list[Character]
) -> list[SharedFiction]:
    alive_ids = {c.id for c in characters if c.is_alive}
    updated = []

    for fiction in fictions:
        if fiction.status == "dead":
            updated.append(fiction)
            continue

        # Remove dead characters from believers
        new_believers = [b for b in fiction.believer_ids if b in alive_ids]

        # Natural spread: try to convert 1-2 non-believers
        if fiction.belief_strength > 40:
            non_believers = [cid for cid in alive_ids if cid not in new_believers]
            spread_count = int(fiction.spread_rate * len(alive_ids))
            for candidate in random.sample(non_believers, min(spread_count, len(non_believers))):
                if random.random() < fiction.spread_rate:
                    new_believers.append(candidate)

        # Update character believed_fiction_ids
        for char in characters:
            if char.id in new_believers and fiction.id not in char.believed_fiction_ids:
                char.believed_fiction_ids.append(fiction.id)
            elif char.id not in new_believers and fiction.id in char.believed_fiction_ids:
                char.believed_fiction_ids.remove(fiction.id)

        # Belief strength decay for non-dominant fictions
        new_strength = fiction.belief_strength
        if fiction.status != "dominant":
            new_strength = max(0, new_strength - 0.5)

        # Determine status
        believer_ratio = len(new_believers) / max(1, len(alive_ids))
        if new_strength <= 5 or len(new_believers) == 0:
            new_status = "dead"
        elif believer_ratio >= 0.6 and new_strength >= 60:
            new_status = "dominant"
        elif believer_ratio >= 0.3:
            new_status = "contested"
        elif new_strength < 30:
            new_status = "declining"
        else:
            new_status = fiction.status

        updated.append(fiction.model_copy(update={
            "believer_ids": new_believers,
            "belief_strength": new_strength,
            "status": new_status,
        }))

    return updated


def apply_fiction_delta(
    fictions: list[SharedFiction],
    characters: list[Character],
    delta: FictionDelta,
) -> tuple[list[SharedFiction], list[Character]]:
    if delta.action == "create":
        new_fiction = SharedFiction(
            id=str(uuid.uuid4()),
            name=delta.new_fiction_name or "Unnamed Myth",
            fiction_type=delta.new_fiction_type or "myth",
            narrative=delta.new_fiction_narrative or "",
            believer_ids=list(delta.target_believer_ids),
            belief_strength=30.0,
            spread_rate=0.05,
            status="emerging",
        )
        for char in characters:
            if char.id in delta.target_believer_ids:
                if new_fiction.id not in char.believed_fiction_ids:
                    char.believed_fiction_ids.append(new_fiction.id)
        return fictions + [new_fiction], characters

    updated = []
    for fiction in fictions:
        if fiction.id != delta.fiction_id:
            updated.append(fiction)
            continue

        new_strength = max(0, min(100, fiction.belief_strength + delta.belief_strength_delta))
        new_believers = list(fiction.believer_ids)

        if delta.action == "spread_to":
            for bid in delta.target_believer_ids:
                if bid not in new_believers:
                    new_believers.append(bid)
                    for char in characters:
                        if char.id == bid and fiction.id not in char.believed_fiction_ids:
                            char.believed_fiction_ids.append(fiction.id)

        elif delta.action == "destroy":
            new_strength = 0
            new_believers = []
            for char in characters:
                if fiction.id in char.believed_fiction_ids:
                    char.believed_fiction_ids.remove(fiction.id)

        new_status = fiction.status
        if new_strength <= 5:
            new_status = "dead"
        elif delta.action == "strengthen" and new_strength > 70:
            new_status = "dominant"
        elif delta.action == "weaken" and new_strength < 40:
            new_status = "contested"

        updated.append(fiction.model_copy(update={
            "belief_strength": new_strength,
            "believer_ids": new_believers,
            "status": new_status,
        }))

    return updated, characters
