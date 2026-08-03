"""Add auth tables and user ownership

Revision ID: e6b30fb48689
Revises: c8acc0e51c14
Create Date: 2026-08-03 16:46:53.883233
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e6b30fb48689'
down_revision: Union[str, None] = 'c8acc0e51c14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Sessions table
    op.create_table('sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_token'), 'sessions', ['token'], unique=True)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)

    # Add user_id to profiles
    with op.batch_alter_table('profiles') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(), nullable=True))
        batch_op.create_foreign_key('fk_profiles_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index('ix_profiles_user_id', ['user_id'])

    # Add user_id to notifications
    with op.batch_alter_table('notifications') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(), nullable=True))
        batch_op.create_foreign_key('fk_notifications_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index('ix_notifications_user_id', ['user_id'])

    # Add indexes on existing FK columns (non-unique for better query performance)
    with op.batch_alter_table('candidates') as batch_op:
        batch_op.create_index('ix_candidates_profile_id', ['profile_id'])

    with op.batch_alter_table('jobs') as batch_op:
        batch_op.create_index('ix_jobs_profile_id', ['profile_id'])

    with op.batch_alter_table('sources') as batch_op:
        batch_op.create_index('ix_sources_profile_id', ['profile_id'])


def downgrade() -> None:
    with op.batch_alter_table('sources') as batch_op:
        batch_op.drop_index('ix_sources_profile_id')

    with op.batch_alter_table('jobs') as batch_op:
        batch_op.drop_index('ix_jobs_profile_id')

    with op.batch_alter_table('candidates') as batch_op:
        batch_op.drop_index('ix_candidates_profile_id')

    with op.batch_alter_table('notifications') as batch_op:
        batch_op.drop_index('ix_notifications_user_id')
        batch_op.drop_constraint('fk_notifications_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('profiles') as batch_op:
        batch_op.drop_index('ix_profiles_user_id')
        batch_op.drop_constraint('fk_profiles_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_token'), table_name='sessions')
    op.drop_table('sessions')