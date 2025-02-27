"""add heybox fields

Revision ID: add_heybox_fields
Create Date: 2024-03-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 添加小黑盒相关字段
    op.add_column('users', sa.Column('heybox_id', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('heybox_nickname', sa.String(80), nullable=True))
    op.add_column('users', sa.Column('heybox_avatar', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('heybox_profile', sa.String(255), nullable=True))

def downgrade():
    # 删除小黑盒相关字段
    op.drop_column('users', 'heybox_profile')
    op.drop_column('users', 'heybox_avatar')
    op.drop_column('users', 'heybox_nickname')
    op.drop_column('users', 'heybox_id') 