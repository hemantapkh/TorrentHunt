"""restrict status values with check constraints

Revision ID: 7446858b5c6c
Revises: 3e6d8e9a1c72
Create Date: 2026-11-26 09:36:59.334262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7446858b5c6c'
down_revision: Union[str, Sequence[str], None] = '3e6d8e9a1c72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Only allow known values in the status columns (CHECK constraints).

    Values are written out here on purpose: a migration is a snapshot and must not
    change when the Python enums do. Adding a value later means a new migration."""
    statuses = "'creator', 'administrator', 'member', 'restricted', 'left', 'kicked'"
    reasons = "'deactivated', 'chat_not_found', 'migrated'"
    sources = "'telegram_update', 'send_error', 'user_activity'"

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_check_constraint('ck_users_chat_status', f"chat_status IN ({statuses})")
        batch_op.create_check_constraint(
            'ck_users_unreachable_reason',
            f"unreachable_reason IS NULL OR unreachable_reason IN ({reasons})",
        )

    with op.batch_alter_table('chat_status_changes', schema=None) as batch_op:
        batch_op.create_check_constraint(
            'ck_chat_status_changes_status', f"status IN ({statuses}, {reasons})",
        )
        batch_op.create_check_constraint(
            'ck_chat_status_changes_source', f"source IN ({sources})",
        )


def downgrade() -> None:
    with op.batch_alter_table('chat_status_changes', schema=None) as batch_op:
        batch_op.drop_constraint('ck_chat_status_changes_source', type_='check')
        batch_op.drop_constraint('ck_chat_status_changes_status', type_='check')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('ck_users_unreachable_reason', type_='check')
        batch_op.drop_constraint('ck_users_chat_status', type_='check')
