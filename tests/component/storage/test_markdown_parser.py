from datetime import UTC, datetime
from pathlib import Path

from tracertm.storage.markdown_parser import ItemData, LinkData


def test_itemdata_round_trip(_tmp_path: Path) -> None:
    item = ItemData(
        id="id1",
        external_id="EXT-1",
        item_type="story",
        status="todo",
        title="Title",
        description="Desc",
        acceptance_criteria=["A", "B"],
        tags=["t1"],
    )

    fm = item.to_frontmatter_dict()
    assert fm["id"] == "id1"
    assert fm["external_id"] == "EXT-1"
    body = item.to_markdown_body()
    assert "Title" in body
    assert "Acceptance Criteria" in body


def test_linkdata_to_from_dict() -> None:
    now = datetime.now(UTC)
    link = LinkData(id="l1", source="s", target="t", link_type="implements", created=now, metadata={"k": "v"})
    data = link.to_dict()
    roundtrip = LinkData.from_dict(data)
    assert roundtrip.id == "l1"
    assert roundtrip.link_type == "implements"
    assert roundtrip.metadata["k"] == "v"
