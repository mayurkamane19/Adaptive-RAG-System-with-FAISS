import hashlib
import secrets
import sqlite3
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings


DB_FILE = Path(settings.DATA_DIR) / "saas_app.db"
PBKDF2_ITERATIONS = 310_000
SESSIONS: dict[str, int] = {}


DEFAULT_AUTH_USERS = [
    ("Demo User", "demo@pulsestack.com", "123456", "admin"),
]

DEFAULT_WORKSPACE_USERS = [
    ("Aisha Khan", "Product Admin", "Active", "India"),
    ("Daniel Reed", "Sales Lead", "Invited", "US"),
    ("Sana Patel", "Support Ops", "Active", "UAE"),
    ("Leo Park", "Finance", "Paused", "Singapore"),
]

DEFAULT_BILLING_ITEMS = [
    ("Pro Annual", "$24,000", "Paid", "14 Apr 2026"),
    ("AI Credits", "$3,200", "Pending", "21 Apr 2026"),
    ("Extra Seats", "$1,480", "Paid", "27 Apr 2026"),
]

DEFAULT_REPORT_RUNS = [
    ("Board Summary", "Scheduled", "Mon"),
    ("Finance Snapshot", "Completed", "Tue"),
    ("Customer Health", "Draft", "Wed"),
]

DEFAULT_NOTIFICATION_ITEMS = [
    ("Payment failure spike", "8 minutes ago - Billing workflow"),
    ("Weekly report delivered", "23 minutes ago - Report builder"),
    ("New admin joined workspace", "1 hour ago - Team access"),
]

DEFAULT_DASHBOARD_GROWTH = [
    ("Jan", 40),
    ("Feb", 52),
    ("Mar", 68),
    ("Apr", 74),
    ("May", 81),
    ("Jun", 92),
]

DEFAULT_ANALYTICS_POINTS = [
    (20, 120),
    (70, 95),
    (120, 105),
    (170, 78),
    (220, 68),
    (280, 42),
]

DEFAULT_REPORT_BARS = [
    ("Mon", 55),
    ("Tue", 78),
    ("Wed", 62),
    ("Thu", 90),
    ("Fri", 73),
    ("Sat", 41),
]


def _connect() -> sqlite3.Connection:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    sql_definition: str,
) -> None:
    if column_name not in _table_columns(connection, table_name):
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_definition}")


def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    password_salt = salt or secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        password_salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    return password_hash, password_salt


def _verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    attempted_hash, _ = _hash_password(password, stored_salt)
    return secrets.compare_digest(attempted_hash, stored_hash)


def _seed_user_data(connection: sqlite3.Connection, owner_user_id: int) -> None:
    connection.executemany(
        """
        INSERT INTO workspace_users (owner_user_id, name, role, status, region)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(owner_user_id, *user) for user in DEFAULT_WORKSPACE_USERS],
    )
    connection.executemany(
        """
        INSERT INTO billing_items (owner_user_id, item, amount, status, invoice_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(owner_user_id, *item) for item in DEFAULT_BILLING_ITEMS],
    )
    connection.executemany(
        """
        INSERT INTO report_runs (owner_user_id, name, status, day_label)
        VALUES (?, ?, ?, ?)
        """,
        [(owner_user_id, *run) for run in DEFAULT_REPORT_RUNS],
    )
    connection.executemany(
        """
        INSERT INTO notification_items (owner_user_id, title, detail)
        VALUES (?, ?, ?)
        """,
        [(owner_user_id, *item) for item in DEFAULT_NOTIFICATION_ITEMS],
    )
    connection.executemany(
        """
        INSERT INTO dashboard_growth (owner_user_id, label, value)
        VALUES (?, ?, ?)
        """,
        [(owner_user_id, *item) for item in DEFAULT_DASHBOARD_GROWTH],
    )
    connection.executemany(
        """
        INSERT INTO analytics_points (owner_user_id, x, y)
        VALUES (?, ?, ?)
        """,
        [(owner_user_id, *item) for item in DEFAULT_ANALYTICS_POINTS],
    )
    connection.executemany(
        """
        INSERT INTO report_bars (owner_user_id, label, value)
        VALUES (?, ?, ?)
        """,
        [(owner_user_id, *item) for item in DEFAULT_REPORT_BARS],
    )


def initialize_saas_db() -> None:
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS auth_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT,
                role TEXT NOT NULL DEFAULT 'member',
                password_hash TEXT,
                password_salt TEXT
            );

            CREATE TABLE IF NOT EXISTS workspace_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                region TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS billing_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL DEFAULT 1,
                item TEXT NOT NULL,
                amount TEXT NOT NULL,
                status TEXT NOT NULL,
                invoice_date TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS report_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                day_label TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notification_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL DEFAULT 1,
                title TEXT NOT NULL,
                detail TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS dashboard_growth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL DEFAULT 1,
                label TEXT NOT NULL,
                value INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS analytics_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL DEFAULT 1,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS report_bars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL DEFAULT 1,
                label TEXT NOT NULL,
                value INTEGER NOT NULL
            );
            """
        )

        _add_column_if_missing(connection, "auth_users", "role", "TEXT NOT NULL DEFAULT 'member'")
        _add_column_if_missing(connection, "auth_users", "password_hash", "TEXT")
        _add_column_if_missing(connection, "auth_users", "password_salt", "TEXT")
        _add_column_if_missing(connection, "workspace_users", "owner_user_id", "INTEGER NOT NULL DEFAULT 1")
        _add_column_if_missing(connection, "billing_items", "owner_user_id", "INTEGER NOT NULL DEFAULT 1")
        _add_column_if_missing(connection, "report_runs", "owner_user_id", "INTEGER NOT NULL DEFAULT 1")
        _add_column_if_missing(connection, "notification_items", "owner_user_id", "INTEGER NOT NULL DEFAULT 1")
        _add_column_if_missing(connection, "dashboard_growth", "owner_user_id", "INTEGER NOT NULL DEFAULT 1")
        _add_column_if_missing(connection, "analytics_points", "owner_user_id", "INTEGER NOT NULL DEFAULT 1")
        _add_column_if_missing(connection, "report_bars", "owner_user_id", "INTEGER NOT NULL DEFAULT 1")

        auth_count = connection.execute("SELECT COUNT(*) FROM auth_users").fetchone()[0]
        if auth_count == 0:
            for full_name, email, password, role in DEFAULT_AUTH_USERS:
                password_hash, password_salt = _hash_password(password)
                connection.execute(
                    """
                    INSERT INTO auth_users (full_name, email, password, role, password_hash, password_salt)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (full_name, email, "", role, password_hash, password_salt),
                )

        users_to_migrate = connection.execute(
            """
            SELECT id, email, password, password_hash, password_salt, role
            FROM auth_users
            """
        ).fetchall()

        for user in users_to_migrate:
            role = "admin" if user["email"] == "demo@pulsestack.com" else (user["role"] or "member")
            if user["password_hash"] and user["password_salt"]:
                connection.execute("UPDATE auth_users SET role = ? WHERE id = ?", (role, user["id"]))
                continue

            source_password = user["password"] or "123456"
            password_hash, password_salt = _hash_password(source_password)
            connection.execute(
                """
                UPDATE auth_users
                SET role = ?, password_hash = ?, password_salt = ?, password = ''
                WHERE id = ?
                """,
                (role, password_hash, password_salt, user["id"]),
            )

        demo_user_id = connection.execute(
            "SELECT id FROM auth_users WHERE email = ?",
            ("demo@pulsestack.com",),
        ).fetchone()["id"]

        for table_name in [
            "workspace_users",
            "billing_items",
            "report_runs",
            "notification_items",
            "dashboard_growth",
            "analytics_points",
            "report_bars",
        ]:
            connection.execute(
                f"UPDATE {table_name} SET owner_user_id = ? WHERE owner_user_id IS NULL OR owner_user_id = 0",
                (demo_user_id,),
            )

        def ensure_seeded(
            table_name: str,
            row_factory,
        ) -> None:
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE owner_user_id = ?",
                (demo_user_id,),
            ).fetchone()[0]
            if count == 0:
                row_factory(connection, demo_user_id)

        ensure_seeded("workspace_users", _seed_user_data)
        # `_seed_user_data` seeds all personal tables at once, so avoid repeating inserts.
        # If workspace rows already existed but some related tables were empty, fill them individually.
        for table_name, rows, sql in [
            ("billing_items", DEFAULT_BILLING_ITEMS, "INSERT INTO billing_items (owner_user_id, item, amount, status, invoice_date) VALUES (?, ?, ?, ?, ?)"),
            ("report_runs", DEFAULT_REPORT_RUNS, "INSERT INTO report_runs (owner_user_id, name, status, day_label) VALUES (?, ?, ?, ?)"),
            ("notification_items", DEFAULT_NOTIFICATION_ITEMS, "INSERT INTO notification_items (owner_user_id, title, detail) VALUES (?, ?, ?)"),
            ("dashboard_growth", DEFAULT_DASHBOARD_GROWTH, "INSERT INTO dashboard_growth (owner_user_id, label, value) VALUES (?, ?, ?)"),
            ("analytics_points", DEFAULT_ANALYTICS_POINTS, "INSERT INTO analytics_points (owner_user_id, x, y) VALUES (?, ?, ?)"),
            ("report_bars", DEFAULT_REPORT_BARS, "INSERT INTO report_bars (owner_user_id, label, value) VALUES (?, ?, ?)"),
        ]:
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE owner_user_id = ?",
                (demo_user_id,),
            ).fetchone()[0]
            if count == 0:
                connection.executemany(sql, [(demo_user_id, *row) for row in rows])


def create_user(full_name: str, email: str, password: str) -> dict[str, str | int]:
    normalized_email = email.lower().strip()
    password_hash, password_salt = _hash_password(password)

    try:
        with _connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO auth_users (full_name, email, password, role, password_hash, password_salt)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (full_name.strip(), normalized_email, "", "member", password_hash, password_salt),
            )
            user_id = cursor.lastrowid
            _seed_user_data(connection, user_id)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists for this email.",
        ) from exc

    return {
        "id": user_id,
        "full_name": full_name.strip(),
        "email": normalized_email,
        "role": "member",
    }


def _serialize_user(row: sqlite3.Row) -> dict[str, str | int]:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "role": row["role"],
    }


def authenticate_user(email: str, password: str) -> tuple[str, dict[str, str | int]]:
    normalized_email = email.lower().strip()
    with _connect() as connection:
        user = connection.execute(
            """
            SELECT id, full_name, email, role, password_hash, password_salt
            FROM auth_users
            WHERE email = ?
            """,
            (normalized_email,),
        ).fetchone()

    if not user or not user["password_hash"] or not user["password_salt"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not _verify_password(password, user["password_hash"], user["password_salt"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = secrets.token_urlsafe(24)
    SESSIONS[token] = user["id"]
    return token, _serialize_user(user)


def get_user_by_token(token: str) -> dict[str, str | int]:
    user_id = SESSIONS.get(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token.",
        )

    with _connect() as connection:
        user = connection.execute(
            "SELECT id, full_name, email, role FROM auth_users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found for this session.",
        )

    return _serialize_user(user)


def clear_session(token: str) -> None:
    SESSIONS.pop(token, None)


def require_role(user: dict[str, str | int], *allowed_roles: str) -> None:
    if user["role"] not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this action.",
        )


def list_workspace_users(owner_user_id: int) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, name, role, status, region
            FROM workspace_users
            WHERE owner_user_id = ?
            ORDER BY id
            """,
            (owner_user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_workspace_user(owner_user_id: int, name: str, role: str, status_value: str, region: str) -> dict:
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO workspace_users (owner_user_id, name, role, status, region)
            VALUES (?, ?, ?, ?, ?)
            """,
            (owner_user_id, name.strip(), role.strip(), status_value.strip(), region.strip()),
        )
        created = connection.execute(
            """
            SELECT id, name, role, status, region
            FROM workspace_users
            WHERE id = ? AND owner_user_id = ?
            """,
            (cursor.lastrowid, owner_user_id),
        ).fetchone()
    return dict(created)


def delete_workspace_user(owner_user_id: int, member_id: int) -> None:
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM workspace_users WHERE id = ? AND owner_user_id = ?",
            (member_id, owner_user_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace user not found.",
            )


def list_billing_items(owner_user_id: int) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, item, amount, status, invoice_date
            FROM billing_items
            WHERE owner_user_id = ?
            ORDER BY id
            """,
            (owner_user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_billing_item(owner_user_id: int, item: str, amount: str, status_value: str, invoice_date: str) -> dict:
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO billing_items (owner_user_id, item, amount, status, invoice_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (owner_user_id, item.strip(), amount.strip(), status_value.strip(), invoice_date.strip()),
        )
        created = connection.execute(
            """
            SELECT id, item, amount, status, invoice_date
            FROM billing_items
            WHERE id = ? AND owner_user_id = ?
            """,
            (cursor.lastrowid, owner_user_id),
        ).fetchone()
    return dict(created)


def delete_billing_item(owner_user_id: int, item_id: int) -> None:
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM billing_items WHERE id = ? AND owner_user_id = ?",
            (item_id, owner_user_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Billing item not found.",
            )


def list_report_runs(owner_user_id: int) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, name, status, day_label
            FROM report_runs
            WHERE owner_user_id = ?
            ORDER BY id
            """,
            (owner_user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_report_run(owner_user_id: int, name: str, status_value: str, day_label: str) -> dict:
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO report_runs (owner_user_id, name, status, day_label)
            VALUES (?, ?, ?, ?)
            """,
            (owner_user_id, name.strip(), status_value.strip(), day_label.strip()),
        )
        created = connection.execute(
            """
            SELECT id, name, status, day_label
            FROM report_runs
            WHERE id = ? AND owner_user_id = ?
            """,
            (cursor.lastrowid, owner_user_id),
        ).fetchone()
    return dict(created)


def delete_report_run(owner_user_id: int, report_id: int) -> None:
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM report_runs WHERE id = ? AND owner_user_id = ?",
            (report_id, owner_user_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report run not found.",
            )


def list_notification_items(owner_user_id: int) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, title, detail
            FROM notification_items
            WHERE owner_user_id = ?
            ORDER BY id
            """,
            (owner_user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_notification_item(owner_user_id: int, title: str, detail: str) -> dict:
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO notification_items (owner_user_id, title, detail)
            VALUES (?, ?, ?)
            """,
            (owner_user_id, title.strip(), detail.strip()),
        )
        created = connection.execute(
            """
            SELECT id, title, detail
            FROM notification_items
            WHERE id = ? AND owner_user_id = ?
            """,
            (cursor.lastrowid, owner_user_id),
        ).fetchone()
    return dict(created)


def delete_notification_item(owner_user_id: int, notification_id: int) -> None:
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM notification_items WHERE id = ? AND owner_user_id = ?",
            (notification_id, owner_user_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification item not found.",
            )


def _list_chart_rows(owner_user_id: int, table_name: str, columns: str) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            f"SELECT {columns} FROM {table_name} WHERE owner_user_id = ? ORDER BY id",
            (owner_user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_dashboard_growth(owner_user_id: int) -> list[dict]:
    return _list_chart_rows(owner_user_id, "dashboard_growth", "label, value")


def list_analytics_points(owner_user_id: int) -> list[dict]:
    return _list_chart_rows(owner_user_id, "analytics_points", "x, y")


def list_report_bars(owner_user_id: int) -> list[dict]:
    return _list_chart_rows(owner_user_id, "report_bars", "label, value")


def get_dashboard_overview(user: dict[str, str | int]) -> dict:
    owner_user_id = int(user["id"])
    return {
        "hero": {
            "arr_value": "$4.8M",
            "arr_hint": "+16.4% vs last quarter",
            "headline": "See revenue, user behavior, and system health in one place.",
            "subtext": f"{user['full_name']} is viewing live workspace metrics from PulseStack.",
        },
        "stats": [
            {"title": "MRR", "value": "$402k", "hint": "+8.2% this month", "tone": "accent"},
            {"title": "Activation Rate", "value": "74%", "hint": "Best in 6 months", "tone": "default"},
            {"title": "Open Incidents", "value": "03", "hint": "2 resolved today", "tone": "default"},
        ],
        "growth_bars": list_dashboard_growth(owner_user_id),
        "accounts": [
            {"id": "r1", "values": ["Northwind", "Enterprise", "$42,000", "Healthy"]},
            {"id": "r2", "values": ["Acme Labs", "Growth", "$18,500", "Review"]},
            {"id": "r3", "values": ["Orbit AI", "Scale", "$29,300", "Healthy"]},
        ],
    }


def get_analytics_overview(user: dict[str, str | int]) -> dict:
    owner_user_id = int(user["id"])
    return {
        "hero": {
            "headline": "Track conversion patterns with deeper funnel intelligence.",
            "subtext": "Compare cohorts, sessions, retention, and campaign ROI without leaving the suite.",
        },
        "stats": [
            {"title": "Sessions", "value": "182k", "hint": "+11% week over week", "tone": "default"},
            {"title": "Bounce Rate", "value": "21%", "hint": "-4% improvement", "tone": "accent"},
            {"title": "Avg. Time", "value": "08:42", "hint": "Per active user", "tone": "default"},
        ],
        "points": list_analytics_points(owner_user_id),
    }


def get_users_overview(user: dict[str, str | int]) -> dict:
    owner_user_id = int(user["id"])
    members = list_workspace_users(owner_user_id)
    active_count = sum(1 for member in members if member["status"].lower() == "active")
    invited_count = sum(1 for member in members if member["status"].lower() == "invited")
    admin_count = sum(1 for member in members if "admin" in member["role"].lower())

    return {
        "hero": {
            "headline": "Manage teams, permissions, and lifecycle stages from one page.",
            "subtext": "Role-based access and onboarding status stay visible for every workspace user.",
        },
        "stats": [
            {"title": "Active Users", "value": str(active_count), "hint": "Private to your account", "tone": "default"},
            {"title": "Pending Invites", "value": str(invited_count), "hint": "Needs follow-up", "tone": "accent"},
            {"title": "Admin Seats", "value": str(admin_count), "hint": f"{len(members)} total team members", "tone": "default"},
        ],
        "rows": [
            {
                "id": str(member["id"]),
                "values": [member["name"], member["role"], member["status"], member["region"]],
            }
            for member in members
        ],
    }


def get_reports_overview(user: dict[str, str | int]) -> dict:
    owner_user_id = int(user["id"])
    runs = list_report_runs(owner_user_id)
    return {
        "hero": {
            "headline": "Create board-ready reports with automated summaries and snapshots.",
            "subtext": "Schedule exports for growth, finance, and customer success in a single workflow.",
        },
        "stats": [
            {"title": "Saved Reports", "value": str(len(runs)), "hint": "Private to your account", "tone": "default"},
            {"title": "Scheduled Runs", "value": str(sum(1 for run in runs if run["status"].lower() == "scheduled")), "hint": "Ready to trigger", "tone": "default"},
            {"title": "Draft Reports", "value": str(sum(1 for run in runs if run["status"].lower() == "draft")), "hint": "Needs review", "tone": "accent"},
        ],
        "bars": list_report_bars(owner_user_id),
        "rows": [
            {
                "id": str(run["id"]),
                "values": [run["name"], run["status"], run["day_label"]],
            }
            for run in runs
        ],
    }


def get_billing_overview(user: dict[str, str | int]) -> dict:
    owner_user_id = int(user["id"])
    items = list_billing_items(owner_user_id)
    pending_count = sum(1 for item in items if item["status"].lower() == "pending")

    return {
        "hero": {
            "headline": "Monitor subscriptions, invoices, and usage caps without friction.",
            "subtext": "Finance teams can review charges, renewals, and credits in one place.",
        },
        "stats": [
            {"title": "Billing Items", "value": str(len(items)), "hint": "Private to your account", "tone": "default"},
            {"title": "Pending Invoices", "value": str(pending_count), "hint": "Needs collection", "tone": "accent"},
            {"title": "Latest Added", "value": items[-1]["amount"] if items else "$0", "hint": items[-1]["item"] if items else "No items yet", "tone": "default"},
        ],
        "rows": [
            {
                "id": str(item["id"]),
                "values": [item["item"], item["amount"], item["status"], item["invoice_date"]],
            }
            for item in items
        ],
    }


def get_notifications_overview(user: dict[str, str | int]) -> dict:
    owner_user_id = int(user["id"])
    items = list_notification_items(owner_user_id)
    return {
        "hero": {
            "headline": "Prioritize operational signals before they become customer issues.",
            "subtext": "All updates, reminders, and incidents are grouped into one action queue.",
        },
        "stats": [
            {"title": "Unread Alerts", "value": str(len(items)), "hint": "Private to your account", "tone": "accent"},
            {"title": "Fresh Alerts", "value": str(min(len(items), 3)), "hint": "Most recent queue", "tone": "default"},
            {"title": "Escalations", "value": str(sum(1 for item in items if "payment" in item["title"].lower())), "hint": "Billing-led signals", "tone": "default"},
        ],
        "items": [
            {"id": str(item["id"]), "title": item["title"], "detail": item["detail"]}
            for item in items
        ],
    }


def get_settings_overview() -> dict:
    return {
        "hero": {
            "headline": "Control branding, environments, and permissions with confidence.",
            "subtext": "Everything sensitive stays grouped into clear configuration zones.",
        },
        "stats": [
            {"title": "API Keys", "value": "12", "hint": "2 expiring soon", "tone": "default"},
            {"title": "Environments", "value": "04", "hint": "Prod, Stage, QA, Demo", "tone": "accent"},
            {"title": "Audit Rules", "value": "31", "hint": "All checks passing", "tone": "default"},
        ],
        "items": [
            {"title": "Branding Kit", "detail": "Logo pack, custom domain, email styling"},
            {"title": "Security Layer", "detail": "SSO, 2FA policy, access review cadence"},
            {"title": "Data Regions", "detail": "Mumbai primary, Frankfurt replica"},
        ],
    }


def get_profile_overview(user: dict[str, str | int]) -> dict:
    initials = "".join(part[:1] for part in str(user["full_name"]).split()[:2]).upper() or "PS"
    return {
        "hero": {
            "headline": "Give every operator a polished workspace identity and focus view.",
            "subtext": "Personal preferences, activity streaks, and performance snapshots live together.",
        },
        "stats": [
            {"title": "Tasks Closed", "value": "146", "hint": "This quarter", "tone": "default"},
            {"title": "Focus Score", "value": "91%", "hint": "Top 8% this week", "tone": "accent"},
            {"title": "Shortcuts", "value": "24", "hint": "Personal automation set", "tone": "default"},
        ],
        "profile": {
            "initials": initials,
            "name": user["full_name"],
            "role": f"{str(user['role']).title()} Workspace User",
            "summary": "Preferences and workspaces are now isolated to your secure account.",
        },
    }
