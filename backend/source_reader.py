"""Bounded-memory UTF-8 source inspection, including very long single lines."""
import hashlib
from functools import lru_cache
from bisect import bisect_left, bisect_right

from .common import AppError


def file_version(target):
    stat = target.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino


@lru_cache(maxsize=16)
def source_index(target, version):
    # About one checkpoint per MiB of text; no full-file contents are cached.
    points = [(0, 1, 0)]
    position, line = 0, 1
    checksum = hashlib.sha256()
    try:
        with target.open("r", encoding="utf-8", newline="") as stream:
            while chunk := stream.read(65536):
                if "\x00" in chunk or "\ufffd" in chunk:
                    raise AppError("仅支持 UTF-8 文本文件。")
                checksum.update(chunk.encode("utf-8"))
                position += len(chunk)
                line += chunk.count("\n")
                if position - points[-1][0] >= 1_048_576:
                    points.append((position, line, stream.tell()))
    except UnicodeError as exc:
        raise AppError("仅支持 UTF-8 文本文件。") from exc
    if version != file_version(target):
        raise AppError("文件在读取期间发生变化，请重新读取。", 409)
    return {"points": points, "chars": position, "lines": line, "digest": checksum.hexdigest()}


def source_page(target, args):
    start = args.get("start_line", 1)
    end = args.get("end_line", start + 199 if type(start) is int else 0)
    cap = args.get("max_chars", 12000)
    requested = args.get("offset")
    if (type(start) is not int or type(end) is not int or start < 1 or end < start or end - start >= 400
            or type(cap) is not int or not 1 <= cap <= 12000
            or requested is not None and (type(requested) is not int or requested < 0)):
        raise AppError("无效的读取范围；每页最多 400 行或 12000 字符。")
    version = file_version(target)
    index = source_index(target, version)
    if requested is not None and requested > index["chars"]:
        raise AppError("字符偏移超出文件范围，请从第一页重新读取。")
    points = index["points"]
    if requested is not None:
        checkpoint = max(0, bisect_right([p[0] for p in points], requested) - 1)
    else:
        # Start before the target line, even when it spans many checkpoints.
        checkpoint = max(0, bisect_left([p[1] for p in points], start) - 1)
    position, line, cookie = points[checkpoint]
    offset, page_line = requested, line
    parts, taken = [], 0
    try:
        with target.open("r", encoding="utf-8", newline="") as stream:
            stream.seek(cookie)
            while chunk := stream.readline(65536):
                if offset is None and line >= start:
                    offset, page_line = position, line
                if offset is not None and position <= offset < position + len(chunk):
                    page_line = line
                if offset is not None and (requested is not None or start <= line <= end):
                    begin = max(0, offset - position)
                    piece = chunk[begin:begin + cap - taken]
                    parts.append(piece)
                    taken += len(piece)
                position += len(chunk)
                line += chunk.count("\n")
                if taken >= cap or requested is None and line > end:
                    break
    except UnicodeError as exc:
        raise AppError("仅支持 UTF-8 文本文件。") from exc
    if version != file_version(target):
        raise AppError("文件在读取期间发生变化，请重新读取。", 409)
    offset = index["chars"] if offset is None else offset
    return {"content": "".join(parts), "offset": offset, "next_offset": offset + taken,
            "total_chars": index["chars"], "total_lines": index["lines"], "start_line": page_line,
            "hasMore": offset + taken < index["chars"], "digest": index["digest"]}


def search_source(target, query, offset=0, budget=2_000_000, limit=60):
    """Search a bounded character window; overlap handles chunk-boundary matches."""
    position, line, consumed = 0, 1, 0
    matches, tail = [], ""
    with target.open("r", encoding="utf-8", newline="") as stream:
        # Read past preceding content without retaining it, preserving line numbers.
        remaining = offset
        while remaining:
            chunk = stream.read(min(65536, remaining))
            if not chunk:
                return [], None, consumed
            line += chunk.count("\n")
            position += len(chunk)
            remaining -= len(chunk)
        while chunk := stream.read(min(65536, budget - consumed + len(query))):
            if "\x00" in chunk or "\ufffd" in chunk:
                raise AppError("仅支持 UTF-8 文本文件。")
            text = tail + chunk
            base = position - len(tail)
            base_line = line - tail.count("\n")
            begin = 0
            while (found := text.find(query, begin)) >= 0:
                absolute = base + found
                if absolute >= offset:
                    matches.append({"line": base_line + text.count("\n", 0, found),
                                    "text": text[max(0, found - 100):found + min(len(query), 200) + 200],
                                    "offset": absolute})
                    if len(matches) >= limit:
                        return matches, absolute + 1, consumed + len(chunk)
                begin = found + 1
            consumed += len(chunk)
            position += len(chunk)
            line += chunk.count("\n")
            tail = text[-(len(query) - 1):] if len(query) > 1 else ""
            if consumed >= budget:
                return matches, position - len(tail), consumed
    return matches, None, consumed
