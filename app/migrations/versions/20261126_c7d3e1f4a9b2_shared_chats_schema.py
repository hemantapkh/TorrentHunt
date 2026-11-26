"""shared chats schema

Moves users to the `chats` table every bot shares (see Orbit): Telegram's names for
columns and values, timestamps with time zone, group titles in `title`, and a generated
`is_reachable`. TorrentHunt-only data moves to its own tables keyed by chat_id:
search counts to `search_stats`, referrers to `referrals`. Tables that pointed at
users.user_id now point at chats.id through a `chat_id` column.

Also drops the legacy insert_default_settings trigger: the app creates settings itself,
and the trigger made every new chat fail with a duplicate settings row.

Revision ID: c7d3e1f4a9b2
Revises: b81f0c5e2a47
Create Date: 2026-11-26 13:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c7d3e1f4a9b2"
down_revision: str | Sequence[str] | None = "b81f0c5e2a47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Written out on purpose: a migration is a snapshot and must not change with the enums.
TYPES = "'private', 'group', 'supergroup', 'channel'"
STATUSES = "'creator', 'administrator', 'member', 'restricted', 'left', 'kicked'"
REASONS = "'deactivated', 'chat_not_found', 'migrated'"
IS_REACHABLE = (
    "status IN ('creator', 'administrator', 'member', 'restricted') AND unreachable_reason IS NULL"
)
TZ = sa.TIMESTAMP(timezone=True)


def _is_pg() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _indexes(table: str) -> set[str]:
    return {i["name"] for i in sa.inspect(op.get_bind()).get_indexes(table)}


def _drop_indexes(table: str, *names: str) -> None:
    """Indexes differ between databases created before Alembic and fresh ones."""
    for name in _indexes(table) & set(names):
        op.drop_index(name, table_name=table)


def _rename(table: str, old: str, new: str) -> None:
    """A plain RENAME COLUMN (Postgres, SQLite 3.25+) also updates foreign keys in other
    tables that point at the column; batch mode's table copy would leave them dangling."""
    op.execute(f"ALTER TABLE {table} RENAME COLUMN {old} TO {new}")


CHAT_RENAMES = [
    ("user_id", "id"),
    ("user_type", "type"),
    ("chat_status", "status"),
    ("chat_status_at", "status_changed_at"),
    ("join_date", "created_at"),
    ("last_active", "last_active_at"),
]
LINKED = ("settings", "bookmarks", "chat_status_changes")


def _cascade(table: str) -> None:
    """Deleting a chat deletes its rows here. Databases from before Alembic already do
    this; fresh ones don't, so their foreign key is replaced."""
    fk = next(f for f in sa.inspect(op.get_bind()).get_foreign_keys(table) if f["referred_table"] == "chats")
    if (fk.get("options") or {}).get("ondelete", "").upper() == "CASCADE":
        return
    name = f"{table}_chat_id_fkey"
    # SQLite foreign keys have no name; this gives the reflected one the name used below.
    with op.batch_alter_table(table, naming_convention={"fk": "%(table_name)s_%(column_0_name)s_fkey"}) as batch_op:
        batch_op.drop_constraint(fk["name"] or name, type_="foreignkey")
        batch_op.create_foreign_key(name, "chats", ["chat_id"], ["id"], ondelete="CASCADE")


def upgrade() -> None:
    if _is_pg():
        op.execute("DROP TRIGGER IF EXISTS user_insert_trigger ON users")
        op.execute("DROP FUNCTION IF EXISTS insert_default_settings()")

    _drop_indexes(
        "users", "ix_users_user_id", "ix_users_join_date", "ix_users_last_active", "ix_users_chat_status",
    )
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("ck_users_chat_status", type_="check")
        batch_op.drop_constraint("ck_users_unreachable_reason", type_="check")
    op.rename_table("users", "chats")
    if _is_pg():
        op.execute("ALTER INDEX IF EXISTS users_pkey RENAME TO chats_pkey")

    for old, new in CHAT_RENAMES:
        _rename("chats", old, new)
    for table in LINKED:  # same rows, column named for what it holds
        _rename(table, "user_id", "chat_id")
    if _is_pg():  # stored as UTC without a time zone until now
        for column in ("created_at", "last_active_at"):
            op.alter_column(
                "chats", column, type_=TZ, existing_type=sa.TIMESTAMP(),
                postgresql_using=f"{column} AT TIME ZONE 'UTC'",
            )
    with op.batch_alter_table("chats") as batch_op:
        batch_op.add_column(sa.Column("title", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("member_count", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("added_by_user_id", sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column("profile_updated_at", TZ, nullable=True))

    # Telegram's spelling of types; group and channel names move to title.
    op.execute("UPDATE chats SET type = lower(type)")
    op.execute("UPDATE chats SET title = first_name, first_name = NULL WHERE type <> 'private'")
    op.execute("UPDATE chats SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    op.create_table(
        "search_stats",
        sa.Column("chat_id", sa.BigInteger(), sa.ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("search_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_search_at", TZ, nullable=True),
    )
    op.execute(
        "INSERT INTO search_stats (chat_id, search_count, last_search_at) "
        "SELECT id, search_count, last_search_at FROM chats "
        "WHERE search_count > 0 OR last_search_at IS NOT NULL"
    )
    op.create_table(
        "referrals",
        sa.Column("chat_id", sa.BigInteger(), sa.ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("referrer", sa.String(), nullable=False),
        sa.Column("created_at", TZ, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.execute(
        "INSERT INTO referrals (chat_id, referrer, created_at) "
        "SELECT id, referrer, created_at FROM chats WHERE referrer IS NOT NULL AND referrer <> ''"
    )

    with op.batch_alter_table("chats", recreate="auto") as batch_op:
        batch_op.drop_column("search_count")
        batch_op.drop_column("last_search_at")
        batch_op.drop_column("referrer")
        batch_op.alter_column("created_at", existing_type=TZ, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))
        batch_op.alter_column("last_active_at", existing_type=TZ, server_default=None)
        batch_op.add_column(sa.Column("is_reachable", sa.Boolean(), sa.Computed(IS_REACHABLE, persisted=True)))
        batch_op.create_check_constraint("ck_chats_type", f"type IN ({TYPES})")
        batch_op.create_check_constraint("ck_chats_status", f"status IN ({STATUSES})")
        batch_op.create_check_constraint(
            "ck_chats_unreachable_reason", f"unreachable_reason IS NULL OR unreachable_reason IN ({REASONS})",
        )
    for column in ("type", "status", "is_reachable", "created_at", "last_active_at"):
        op.create_index(f"ix_chats_{column}", "chats", [column])

    _drop_indexes("settings", "ix_settings_user_id")
    _drop_indexes("bookmarks", "ix_bookmarks_user_id")
    op.create_index("ix_bookmarks_chat_id", "bookmarks", ["chat_id"])
    _drop_indexes("chat_status_changes", "ix_chat_status_changes_user_id")
    op.create_index("ix_chat_status_changes_chat_id", "chat_status_changes", ["chat_id"])
    if _is_pg():  # foreign keys follow the renames; give them matching names
        for table in LINKED:
            op.execute(
                f"ALTER TABLE {table} RENAME CONSTRAINT {table}_user_id_fkey TO {table}_chat_id_fkey"
            )
    for table in ("settings", "bookmarks"):
        _cascade(table)


def downgrade() -> None:
    if _is_pg():
        for table in LINKED:
            op.execute(
                f"ALTER TABLE {table} RENAME CONSTRAINT {table}_chat_id_fkey TO {table}_user_id_fkey"
            )
    op.drop_index("ix_chat_status_changes_chat_id", table_name="chat_status_changes")
    op.drop_index("ix_bookmarks_chat_id", table_name="bookmarks")

    for column in ("type", "status", "is_reachable", "created_at", "last_active_at"):
        op.drop_index(f"ix_chats_{column}", table_name="chats")
    with op.batch_alter_table("chats", recreate="auto") as batch_op:
        batch_op.drop_constraint("ck_chats_type", type_="check")
        batch_op.drop_constraint("ck_chats_status", type_="check")
        batch_op.drop_constraint("ck_chats_unreachable_reason", type_="check")
        batch_op.drop_column("is_reachable")
        batch_op.add_column(sa.Column("search_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("last_search_at", TZ, nullable=True))
        batch_op.add_column(sa.Column("referrer", sa.String(), nullable=True))
    op.execute(
        "UPDATE chats SET search_count = s.search_count, last_search_at = s.last_search_at "
        "FROM search_stats s WHERE s.chat_id = chats.id"
        if _is_pg()
        else "UPDATE chats SET search_count = (SELECT search_count FROM search_stats s WHERE s.chat_id = chats.id), "
        "last_search_at = (SELECT last_search_at FROM search_stats s WHERE s.chat_id = chats.id) "
        "WHERE id IN (SELECT chat_id FROM search_stats)"
    )
    op.execute(
        "UPDATE chats SET referrer = (SELECT referrer FROM referrals r WHERE r.chat_id = chats.id) "
        "WHERE id IN (SELECT chat_id FROM referrals)"
    )
    op.drop_table("referrals")
    op.drop_table("search_stats")
    op.execute("UPDATE chats SET first_name = title WHERE type <> 'private' AND first_name IS NULL")
    op.execute("UPDATE chats SET type = upper(type)")

    with op.batch_alter_table("chats") as batch_op:
        batch_op.drop_column("profile_updated_at")
        batch_op.drop_column("added_by_user_id")
        batch_op.drop_column("member_count")
        batch_op.drop_column("title")
        batch_op.alter_column("created_at", existing_type=TZ, nullable=True)
        batch_op.alter_column("last_active_at", existing_type=TZ, server_default=sa.text("CURRENT_TIMESTAMP"))
    if _is_pg():
        for column in ("created_at", "last_active_at"):
            op.alter_column(
                "chats", column, type_=sa.TIMESTAMP(), existing_type=TZ,
                postgresql_using=f"{column} AT TIME ZONE 'UTC'",
            )
    for table in LINKED:
        _rename(table, "chat_id", "user_id")
    for old, new in CHAT_RENAMES:
        _rename("chats", new, old)
    op.create_index("ix_chat_status_changes_user_id", "chat_status_changes", ["user_id"])
    if _is_pg():
        op.execute("ALTER INDEX IF EXISTS chats_pkey RENAME TO users_pkey")
    op.rename_table("chats", "users")
    with op.batch_alter_table("users") as batch_op:
        batch_op.create_check_constraint("ck_users_chat_status", f"chat_status IN ({STATUSES})")
        batch_op.create_check_constraint(
            "ck_users_unreachable_reason", f"unreachable_reason IS NULL OR unreachable_reason IN ({REASONS})",
        )
    op.create_index("ix_users_chat_status", "users", ["chat_status"])
    op.create_index("ix_users_last_active", "users", ["last_active"])
    # The legacy settings trigger isn't restored: it broke sign-ups (see upgrade).
