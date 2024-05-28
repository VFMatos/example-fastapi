"""add fk to posts table

Revision ID: bb09fc2cca97
Revises: a16d6dcbf397
Create Date: 2024-05-27 21:49:32.337015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bb09fc2cca97'
down_revision: Union[str, None] = 'a16d6dcbf397'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('posts') as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_posts_owner_id_users_id',
                                    referent_table='users',
                                    local_cols=['owner_id'], remote_cols=['id'],
                                    ondelete="CASCADE")

    pass


def downgrade() -> None:
    with op.batch_alter_table('posts') as batch_op:
        batch_op.drop_constraint('fk_posts_owner_id_users_id', type_='foreignkey')
        batch_op.drop_column('owner_id')

    pass
