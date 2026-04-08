import re
import sqlite3


def _normalize(sql: str) -> str:
    return " ".join(sql.lower().strip().split())


def _extract_tables(sql: str) -> set[str]:
    return set(re.findall(r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.IGNORECASE))


def _extract_table_columns(sql: str) -> dict[str, set[str]]:
    table_cols: dict[str, set[str]] = {}
    for table, col in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b", sql):
        table_cols.setdefault(table, set()).add(col)
    return table_cols


def _build_sandbox_db(expected_sql: str, action_sql: str) -> sqlite3.Connection:
    def q(identifier: str) -> str:
        return '"' + identifier.replace('"', '""') + '"'

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    tables = _extract_tables(expected_sql) | _extract_tables(action_sql)
    table_columns = _extract_table_columns(expected_sql)
    action_cols = _extract_table_columns(action_sql)

    for table, cols in action_cols.items():
        table_columns.setdefault(table, set()).update(cols)

    # Common fallback columns to keep sandbox robust for simple SQL tasks.
    fallback_cols = {
        "id",
        "name",
        "age",
        "email",
        "price",
        "cost",
        "quantity",
        "salary",
        "marks",
        "amount",
        "error_code",
        "stock",
        "value",
        "count",
        "duration",
        "user_id",
        "customer_id",
        "student_id",
        "author_id",
        "order_id",
        "emp_id",
        "acc_id",
        "teacher_id",
        "team_id",
        "product_id",
        "vendor_id",
        "city",
        "status",
        "title",
        "model",
        "score",
    }

    for table in tables:
        cols = set(table_columns.get(table, set()))
        cols.update(fallback_cols)
        if "id" not in cols:
            cols.add("id")

        col_defs = ", ".join([f"{col} TEXT" for col in sorted(cols)])
        cur.execute(f"CREATE TABLE IF NOT EXISTS {q(table)} ({col_defs});")

        values = {col: "1" for col in cols}
        if "name" in values:
            values["name"] = "alice"
        if "age" in values:
            values["age"] = "20"
        if "status" in values:
            values["status"] = "shipped"

        insert_cols = ", ".join(sorted(values.keys()))
        placeholders = ", ".join(["?"] * len(values))
        cur.execute(
            f"INSERT INTO {q(table)} ({insert_cols}) VALUES ({placeholders});",
            [values[col] for col in sorted(values.keys())],
        )

    conn.commit()
    return conn


def grade(task: dict, action_sql: str) -> tuple[float, str | None]:
    expected_sql = task["expected"]
    expected = _normalize(expected_sql)
    action = _normalize(action_sql)

    if action == expected:
        return 1.0, None

    expected_tokens = expected.split()
    action_tokens = action.split()
    overlap_ratio = (sum(1 for token in expected_tokens if token in action_tokens) / len(expected_tokens)) if expected_tokens else 0.0

    conn = _build_sandbox_db(expected_sql, action_sql)
    cur = conn.cursor()

    try:
        expected_rows = cur.execute(expected_sql).fetchall()
    except sqlite3.Error:
        # Fallback: if expected query fails in sandbox, keep old token-based scoring.
        conn.close()
        return overlap_ratio * 0.8, "Reference query failed in sandbox."

    try:
        action_rows = cur.execute(action_sql).fetchall()
    except sqlite3.Error as e:
        conn.close()
        # Invalid SQL still gets partial token reward for incremental learning signal.
        return overlap_ratio * 0.5, f"Execution Error: {e}"

    conn.close()

    if action_rows == expected_rows:
        # Semantically correct on sandbox data, but not exact string match.
        return max(0.9, overlap_ratio), "Semantically correct but formatting/token differences remain."

    # Executable query with wrong result: give meaningful partial credit.
    return min(0.8, 0.3 + (overlap_ratio * 0.5)), "Query executed but result did not match expected output."
