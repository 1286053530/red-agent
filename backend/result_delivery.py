"""Validate optional topic cards without changing completion requirements."""

from .common import AppError


def result_cards(args):
    if "cards" not in args:
        return []
    cards = args["cards"]
    if not isinstance(cards, list) or not 1 <= len(cards) <= 8:
        raise AppError("cards 须包含 1—8 张主题卡片；简短结果可省略该字段。")
    result = []
    for card in cards:
        if not isinstance(card, dict) or set(card) != {"title", "items"}:
            raise AppError("每张卡片只包含 title 和 items。")
        title, items = card["title"], card["items"]
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80:
            raise AppError("卡片标题须为 1—80 字的非空文本。")
        if not isinstance(items, list) or not 1 <= len(items) <= 8 or any(
            not isinstance(item, str) or not 1 <= len(item.strip()) <= 1500 for item in items
        ):
            raise AppError("卡片 items 须包含 1—8 条非空文本，每条不超过 1500 字。")
        result.append({"title": title.strip(), "items": [item.strip() for item in items]})
    return result


def result_message(result):
    parts = [result["summary"]]
    for index, card in enumerate(result.get("cards", []), 1):
        parts.append(f"{index}. {card['title']}\n" + "\n".join("- " + item for item in card["items"]))
    parts.append("验证依据：" + result["evidence"])
    return "\n\n".join(parts)
