import re
from backend.markdown_utils import align_tables_in_text


def find_first_table(lines):
    """Return (start_index, sep_index, end_index) of first pipe-table in lines or None."""
    for idx in range(len(lines) - 1):
        if '|' not in lines[idx]:
            continue
        # look for separator on next meaningful line
        j = idx + 1
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        if j < len(lines) and re.search(r'-{1,}', lines[j]) and '|' in lines[j]:
            # found separator-ish line
            # collect end
            k = j + 1
            while k < len(lines) and '|' in lines[k]:
                k += 1
            return idx, j, k
    return None


def test_align_basic_table_widths():
    md = (
        "| H | LongHeader | M |\n"
        "|--|:--:|--:|\n"
        "| a | bb | ccc |\n"
        "| xxxx | y | z |\n"
    )

    out = align_tables_in_text(md)
    lines = out.splitlines()
    found = find_first_table(lines)
    assert found is not None
    start, sep, end = found
    # header is start, data rows are sep+1..end-1
    header = lines[start]
    data_rows = lines[sep+1:end]
    # To verify alignment reliably, compare column pipe positions across rows
    table_lines = [header] + data_rows
    pipe_positions = [ [i for i,ch in enumerate(r) if ch == '|'] for r in table_lines ]
    # All rows should have the same number of pipes and the same positions
    first = pipe_positions[0]
    for pp in pipe_positions[1:]:
        assert len(pp) == len(first)
        assert pp == first


def test_preserve_fenced_code_blocks():
    md = (
        "Here is a code block:\n\n"
        "```\n"
        "| not | a | table |\n"
        "| --- | --- | --- |\n"
        "| should | remain | unchanged |\n"
        "```\n\n"
        "And a real table:\n\n"
        "| A | B |\n"
        "|---|---|\n"
        "|1|2|\n"
    )

    out = align_tables_in_text(md)
    # code fence should remain intact and not be aligned
    assert '```\n| not | a | table |' in out
    # the real table should be aligned (separator row present)
    assert re.search(r"\|\s*-{1,}\s*\|\s*-{1,}\s*\|", out)


def test_handles_tables_without_trailing_pipes():
    md = (
        "| X | Y\n"
        "|---|---\n"
        "| one | two\n"
    )
    out = align_tables_in_text(md)
    # ensure output still contains pipe separators and a separator row
    assert '|' in out
    # find first table and check the separator line contains dashes
    lines = out.splitlines()
    found = find_first_table(lines)
    assert found is not None
    start, sep, end = found
    sep_line = lines[sep]
    assert '-' in sep_line


def test_idempotent_alignment():
    md = (
        "| A | B | C |\n"
        "|---|:--:|--:|\n"
        "| one | two | three |\n"
        "| four | five | six |\n"
    )
    first = align_tables_in_text(md)
    second = align_tables_in_text(first)
    assert first == second


def test_center_and_right_alignment_respected():
    md = (
        "| L | C | R |\n"
        "|:--|:--:|--:|\n"
        "| left | center | right |\n"
        "| l | cc | rrr |\n"
    )
    out = align_tables_in_text(md)
    lines = out.splitlines()
    found = find_first_table(lines)
    assert found is not None
    start, sep, end = found
    # check that separator row contains colon patterns for center/left/right
    sep_line = lines[sep]
    assert sep_line.count(':') >= 2
    # Verify pipe positions equal across table rows
    table_lines = [lines[start]] + lines[sep+1:end]
    pipe_positions = [[i for i,ch in enumerate(r) if ch == '|'] for r in table_lines]
    assert all(pp == pipe_positions[0] for pp in pipe_positions)


def test_empty_cells_and_inconsistent_row_lengths():
    md = (
        "| H1 | H2 | H3 |\n"
        "|---|---|---|\n"
        "| a |  | c |\n"
        "| longtext | b | |\n"
        "| x | y | z |\n"
    )
    out = align_tables_in_text(md)
    lines = out.splitlines()
    found = find_first_table(lines)
    assert found is not None
    start, sep, end = found
    table_lines = [lines[start]] + lines[sep+1:end]
    # Ensure pipe columns line up
    pipe_positions = [[i for i,ch in enumerate(r) if ch == '|'] for r in table_lines]
    assert all(pp == pipe_positions[0] for pp in pipe_positions)
