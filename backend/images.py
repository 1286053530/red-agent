"""User supplied image attachments, stored outside the compact conversation state."""
import base64
import binascii
import re

from .common import AppError

MAX_IMAGES = 4
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 12 * 1024 * 1024
IMAGE_REQUEST_BYTES = 17 * 1024 * 1024


def validate_images(images):
    if images is None:
        return []
    if not isinstance(images, list) or len(images) > MAX_IMAGES:
        raise AppError("每条消息最多添加 4 张图片。")
    result, total = [], 0
    for image in images:
        if not isinstance(image, dict) or not isinstance(image.get("dataUrl"), str):
            raise AppError("图片参数无效。")
        value = image["dataUrl"]
        if len(value) > (MAX_IMAGE_BYTES + 2) // 3 * 4 + 64:
            raise AppError("单张图片不能超过 5 MB。")
        match = re.fullmatch(r"data:(image/(?:png|jpeg|webp));base64,([A-Za-z0-9+/=]+)", value)
        if not match:
            raise AppError("仅支持 PNG、JPEG 和 WebP 图片的 Base64 数据。")
        try:
            raw = base64.b64decode(match[2], validate=True)
        except (ValueError, binascii.Error) as exc:
            raise AppError("图片数据无效。") from exc
        mime = match[1]
        valid = (mime == "image/png" and raw.startswith(b"\x89PNG\r\n\x1a\n")
                 or mime == "image/jpeg" and raw.startswith(b"\xff\xd8\xff")
                 or mime == "image/webp" and raw.startswith(b"RIFF") and raw[8:12] == b"WEBP")
        if not valid:
            raise AppError("图片内容与格式不一致。")
        total += len(raw)
        if len(raw) > MAX_IMAGE_BYTES or total > MAX_TOTAL_BYTES:
            raise AppError("单张图片不超过 5 MB，每条消息图片合计不超过 12 MB。")
        name = image.get("name")
        result.append(({"name": name[:120] if isinstance(name, str) else "图片", "mime": mime, "size": len(raw)}, raw))
    return result


def image_content(text, images):
    return ([{"type": "text", "text": text}] if text else []) + [
        {"type": "image_url", "image_url": {"url": image["dataUrl"]}} for image in images
    ]
