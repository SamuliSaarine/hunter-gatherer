from game.state import GameState, Season

SEASON_ORDER = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
DAYS_PER_SEASON = 30


def advance_time(state: GameState) -> GameState:
    new_day = state.current_day + 1
    new_season = state.current_season
    new_year = state.current_year

    if new_day > DAYS_PER_SEASON:
        new_day = 1
        current_idx = SEASON_ORDER.index(state.current_season)
        next_idx = (current_idx + 1) % len(SEASON_ORDER)
        new_season = SEASON_ORDER[next_idx]
        if next_idx == 0:
            new_year += 1

    return state.model_copy(update={
        "current_day": new_day,
        "current_season": new_season,
        "current_year": new_year,
    })
