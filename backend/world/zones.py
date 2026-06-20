from game.state import Zone


def create_starting_world() -> list[Zone]:
    return [
        Zone(
            id="camp",
            name="The Camp",
            zone_type="camp",
            resources={"food": 30.0, "wood": 20.0, "stone": 10.0, "medicine": 15.0, "hides": 8.0},
            danger_level=0.05,
            connected_zone_ids=["hunting_grounds", "berry_meadow", "river_ford"],
            description="A sheltered hollow between two granite outcrops. The band's hearth smolders here day and night. Ochre handprints mark the largest stone.",
        ),
        Zone(
            id="hunting_grounds",
            name="The Hunting Grounds",
            zone_type="forest",
            resources={"food": 60.0, "wood": 50.0, "hides": 25.0, "stone": 5.0, "medicine": 10.0},
            danger_level=0.35,
            connected_zone_ids=["camp", "eastern_ridge", "dark_thicket"],
            description="Dense oak and pine forest threaded with deer trails. The undergrowth is thick enough to hide a crouching hunter — or a predator.",
        ),
        Zone(
            id="river_ford",
            name="The River Ford",
            zone_type="river",
            resources={"food": 45.0, "wood": 15.0, "stone": 20.0, "medicine": 20.0, "hides": 5.0},
            danger_level=0.2,
            connected_zone_ids=["camp", "berry_meadow", "sacred_grove"],
            description="A wide shallow crossing where the river spreads over flat stones. Fish dart in the shallows. The opposite bank belongs to no one — or everyone.",
        ),
        Zone(
            id="eastern_ridge",
            name="The Eastern Ridge",
            zone_type="hills",
            resources={"food": 20.0, "wood": 10.0, "stone": 40.0, "medicine": 8.0, "hides": 3.0},
            danger_level=0.25,
            connected_zone_ids=["hunting_grounds", "dark_thicket"],
            description="A long spine of exposed rock with a view of three days' travel in every direction. Strange lights have been seen here at dusk. The wind never stops.",
        ),
        Zone(
            id="berry_meadow",
            name="The Berry Meadow",
            zone_type="plains",
            resources={"food": 55.0, "wood": 5.0, "stone": 5.0, "medicine": 30.0, "hides": 2.0},
            danger_level=0.1,
            connected_zone_ids=["camp", "river_ford"],
            description="Open grassland edged with hawthorn and elder. In spring and summer it is thick with fruit. In winter, only dry stalks and frozen mud.",
        ),
        Zone(
            id="sacred_grove",
            name="The Sacred Grove",
            zone_type="sacred_ground",
            resources={"food": 15.0, "wood": 30.0, "stone": 5.0, "medicine": 40.0, "hides": 0.0},
            danger_level=0.08,
            connected_zone_ids=["river_ford", "dark_thicket"],
            description="Ancient yew trees whose trunks are older than any living memory. The band comes here to bury the dead and mark the turning of seasons. Something listens here — or so Mara says.",
        ),
        Zone(
            id="dark_thicket",
            name="The Dark Thicket",
            zone_type="forest",
            resources={"food": 35.0, "wood": 60.0, "stone": 8.0, "medicine": 25.0, "hides": 15.0},
            danger_level=0.7,
            connected_zone_ids=["hunting_grounds", "eastern_ridge", "sacred_grove"],
            description="A tangled mass of briar, deadfall, and shadow that no one enters willingly. There are tracks here that do not belong to anything the band has named. The trees grow wrong.",
        ),
    ]
