from game.state import GameState


def build_context(state: GameState) -> str:
    player = next((c for c in state.characters if c.is_player), None)
    if not player:
        return "No player found."

    current_zone = next((z for z in state.world_zones if z.id == player.current_zone_id), None)
    zone_name = current_zone.name if current_zone else player.current_zone_id
    zone_desc = current_zone.description if current_zone else ""

    # Connected zones
    connected = []
    if current_zone:
        for zid in current_zone.connected_zone_ids:
            z = next((z for z in state.world_zones if z.id == zid), None)
            if z:
                connected.append(z.name)

    # NPCs in same zone
    nearby_npcs = [
        c for c in state.characters
        if not c.is_player and c.is_alive and c.current_zone_id == player.current_zone_id
    ]

    # Top skills
    top_skills = sorted(player.skills.items(), key=lambda x: x[1], reverse=True)[:3]
    skills_str = ", ".join(f"{k} {v}" for k, v in top_skills) or "none yet"

    # Active fictions
    active_fictions = [f for f in state.shared_fictions if f.status != "dead"]

    # Recent events (last 5)
    recent = state.recent_events[-5:] if state.recent_events else []

    lines = [
        "=== WORLD STATE ===",
        f"Season: {state.current_season.value.upper()}, Day {state.current_day}, Year {state.current_year}",
        f"Turn: {state.current_turn} | Difficulty: {state.difficulty}",
        "",
        "=== PLAYER ===",
        f"Name: {player.name}, Age: {player.age}",
        f"Health: {player.health:.0f}/100 | Hunger: {player.hunger:.0f}/100 | Fatigue: {player.fatigue:.0f}/100 | Reputation: {player.reputation:.0f}/100",
        f"STR {player.strength} | END {player.endurance} | PER {player.perception} | LANG {player.language} | ABS {player.abstraction} | MEM {player.memory}",
        f"Skills: {skills_str}",
        f"Current Zone: {zone_name} — {zone_desc}",
        f"Paths out: {', '.join(connected) if connected else 'none'}",
        f"Believes in: {', '.join(f.name for f in active_fictions if player.id in f.believer_ids) or 'nothing currently'}",
        "",
        f"=== BAND: {state.band.name} ===",
        f"Cohesion: {state.band.belief_cohesion:.0f}/100 | Tension: {state.band.internal_tension:.0f}/100 | Shared Food: {state.band.shared_food:.0f}",
        f"Members in your zone ({len(nearby_npcs)}):",
    ]

    for npc in nearby_npcs[:6]:
        lines.append(f"  - {npc.name}, age {npc.age}: {npc.personality}")

    if not nearby_npcs:
        lines.append("  (you are alone here)")

    lines += ["", "=== ACTIVE MYTHS ==="]
    for f in active_fictions[:4]:
        believer_count = len(f.believer_ids)
        total = len(state.band.member_ids)
        lines.append(
            f"  {f.name} ({f.fiction_type}, {f.status}): "
            f"{f.narrative[:90]}{'...' if len(f.narrative) > 90 else ''} "
            f"[{believer_count}/{total} believers, strength {f.belief_strength:.0f}]"
        )

    if not active_fictions:
        lines.append("  (no active myths)")

    lines += ["", "=== RECENT EVENTS ==="]
    for event in recent:
        lines.append(f"  {event}")
    if not recent:
        lines.append("  (none yet)")

    # Character IDs for delta parsing (short form)
    lines += ["", "=== CHARACTER IDs (for delta output) ==="]
    for c in state.characters:
        lines.append(f"  {c.id}: {c.name} (player={c.is_player})")

    lines += ["", "=== FICTION IDs ==="]
    for f in state.shared_fictions:
        lines.append(f"  {f.id}: {f.name}")

    lines += ["", "=== ZONE IDs ==="]
    for z in state.world_zones:
        lines.append(f"  {z.id}: {z.name}")

    return "\n".join(lines)
