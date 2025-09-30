"""Small markdown utilities for the backend.

Provide align_tables_in_text(text) which aligns pipe-style Markdown tables so
the raw returned Markdown looks well-formatted when viewed as plain text.
"""
import re
from typing import List


def split_pipe_row(line: str) -> List[str] | None:
    if '|' not in line:
        return None
    s = line.rstrip('\n')
    s_stripped = s.strip()
    if s_stripped == '':
        return None
    core = s_stripped
    if core.startswith('|') and core.endswith('|'):
        core = core[1:-1]
    elif core.startswith('|'):
        core = core[1:]
    elif core.endswith('|'):
        core = core[:-1]
    parts = [p.strip() for p in core.split('|')]
    return parts


def is_separator_cell(token: str) -> bool:
    token = token.strip()
    return re.match(r'^:?-{3,}:?$', token) is not None


def is_separator_row(line: str) -> bool:
    parts = split_pipe_row(line)
    if parts is None:
        return False
    return all(is_separator_cell(p) for p in parts)


def detect_indent(line: str) -> str:
    m = re.match(r'^(\s*)', line)
    return m.group(1) if m else ''


def format_separator_token(width: int, align: str) -> str:
    dashes = max(3, width)
    if align == 'center':
        if dashes >= 2:
            return ':' + ('-' * (dashes - 2)) + ':'
        else:
            return ':--:'
    elif align == 'right':
        return ('-' * (dashes - 1)) + ':'
    else:
        return ':' + ('-' * (dashes - 1)) if align == 'left' else ('-' * dashes)


def detect_alignment_from_sep(token: str) -> str:
    t = token.strip()
    left = t.startswith(':')
    right = t.endswith(':')
    if left and right:
        return 'center'
    if right:
        return 'right'
    if left:
        return 'left'
    return 'left'


def align_table_block(lines: List[str]) -> List[str]:
    if len(lines) < 2:
        return lines
    indent = detect_indent(lines[0])
    parsed_rows = []
    for ln in lines:
        parts = split_pipe_row(ln)
        if parts is None:
            parsed_rows.append([])
        else:
            parsed_rows.append(parts)

    sep_idx = None
    for i, ln in enumerate(lines):
        if is_separator_row(ln):
            sep_idx = i
            break
    if sep_idx is None:
        return lines

    ncols = max(len(r) for r in parsed_rows)
    for r in parsed_rows:
        if len(r) < ncols:
            r.extend([''] * (ncols - len(r)))

    widths = [0] * ncols
    for i, r in enumerate(parsed_rows):
        if i == sep_idx:
            continue
        for j, cell in enumerate(r):
            widths[j] = max(widths[j], len(cell))

    sep_parts = parsed_rows[sep_idx]
    alignments = []
    for j in range(ncols):
        token = sep_parts[j] if j < len(sep_parts) else '---'
        alignments.append(detect_alignment_from_sep(token))

    out_lines = []
    for i, r in enumerate(parsed_rows):
        if i == sep_idx:
            cells = []
            for j in range(ncols):
                tok = format_separator_token(widths[j], alignments[j])
                cells.append(tok)
            out_lines.append(indent + '| ' + ' | '.join(cells) + ' |')
        else:
            cells = []
            for j, cell in enumerate(r):
                w = widths[j]
                align = alignments[j]
                if align == 'right':
                    txt = cell.rjust(w)
                elif align == 'center':
                    txt = cell.center(w)
                else:
                    txt = cell.ljust(w)
                cells.append(txt)
            out_lines.append(indent + '| ' + ' | '.join(cells) + ' |')

    return out_lines


def align_tables_in_text(text: str) -> str:
    lines = text.splitlines()
    out_lines: List[str] = []
    i = 0
    in_fence = False
    fence_marker = '```'
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith(fence_marker):
            in_fence = not in_fence
            out_lines.append(line)
            i += 1
            continue

        if in_fence:
            out_lines.append(line)
            i += 1
            continue

        if '|' in line:
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines) and is_separator_row(lines[j]):
                k = i
                table_block = []
                while k < len(lines) and '|' in lines[k]:
                    table_block.append(lines[k])
                    k += 1
                aligned = align_table_block(table_block)
                out_lines.extend(aligned)
                i = k
                continue

        out_lines.append(line)
        i += 1

    return '\n'.join(out_lines) + ('\n' if text.endswith('\n') else '')
