from app.schemas import MediaItem, Category


def get_all_mock_items() -> list[MediaItem]:
    return [
        MediaItem(
            id=1,
            title="Interstellar",
            category="movie",
            year=2014,
            genres=["Sci-Fi", "Drama"],
            description="Фільм про космічну подорож, виживання людства та пошук нового дому.",
        ),
        MediaItem(
            id=2,
            title="Inception",
            category="movie",
            year=2010,
            genres=["Sci-Fi", "Thriller"],
            description="Історія про проникнення у сни та маніпуляцію ідеями.",
        ),
        MediaItem(
            id=3,
            title="Breaking Bad",
            category="series",
            year=2008,
            genres=["Crime", "Drama"],
            description="Серіал про вчителя хімії, який занурюється у кримінальний світ.",
        ),
        MediaItem(
            id=4,
            title="Dark",
            category="series",
            year=2017,
            genres=["Sci-Fi", "Mystery"],
            description="Похмурий серіал про час, сімейні таємниці й зникнення дітей.",
        ),
        MediaItem(
            id=5,
            title="1984",
            category="book",
            year=1949,
            genres=["Dystopian", "Political Fiction"],
            description="Роман про тоталітарну державу, контроль і втрату свободи.",
        ),
        MediaItem(
            id=6,
            title="Dune",
            category="book",
            year=1965,
            genres=["Sci-Fi", "Adventure"],
            description="Епічний науково-фантастичний роман про владу, ресурси та пророцтво.",
        ),
    ]


def get_mock_items(category: Category | None = None) -> list[MediaItem]:
    items = get_all_mock_items()

    if category is None:
        return items

    return [item for item in items if item.category == category]


def get_mock_item_by_id(item_id: int) -> MediaItem | None:
    items = get_all_mock_items()

    for item in items:
        if item.id == item_id:
            return item

    return None