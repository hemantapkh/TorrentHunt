"""allow lookup as a status source

Revision ID: b81f0c5e2a47
Revises: 7446858b5c6c
Create Date: 2026-11-26 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b81f0c5e2a47'
down_revision: Union[str, Sequence[str], None] = '7446858b5c6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD = "'telegram_update', 'send_error', 'user_activity'"
NEW = f"{OLD}, 'lookup'"


def _replace(sources: str) -> None:
    with op.batch_alter_table('chat_status_changes', schema=None) as batch_op:
        batch_op.drop_constraint('ck_chat_status_changes_source', type_='check')
        batch_op.create_check_constraint(
            'ck_chat_status_changes_source', f"source IN ({sources})",
        )


def upgrade() -> None:
    _replace(NEW)


def downgrade() -> None:
    op.execute("DELETE FROM chat_status_changes WHERE source = 'lookup'")
    _replace(OLD)
