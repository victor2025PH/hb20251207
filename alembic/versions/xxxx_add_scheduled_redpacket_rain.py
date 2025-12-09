"""add scheduled_redpacket_rains table

Revision ID: xxxx_add_scheduled_redpacket_rain
Revises: 
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'xxxx_add_scheduled_redpacket_rain'
down_revision = None  # 请根据实际情况修改
branch_labels = None
depends_on = None


def upgrade():
    # 创建 scheduled_redpacket_rains 表
    op.create_table(
        'scheduled_redpacket_rains',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('total_amount', sa.Numeric(20, 8), nullable=False),
        sa.Column('currency', sa.Enum('USDT', 'TON', 'STARS', 'POINTS', name='currencytype'), nullable=False),
        sa.Column('packet_count', sa.Integer(), nullable=False),
        sa.Column('target_chat_id', sa.BigInteger(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('packet_type', sa.Enum('RANDOM', 'EQUAL', 'EXCLUSIVE', name='redpackettype'), nullable=True),
        sa.Column('status', sa.String(32), nullable=True, server_default='scheduled'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_scheduled_rain_start_time', 'scheduled_redpacket_rains', ['start_time'])
    op.create_index('ix_scheduled_rain_status', 'scheduled_redpacket_rains', ['status'])
    op.create_index(op.f('ix_scheduled_redpacket_rains_target_chat_id'), 'scheduled_redpacket_rains', ['target_chat_id'])


def downgrade():
    # 删除索引
    op.drop_index(op.f('ix_scheduled_redpacket_rains_target_chat_id'), table_name='scheduled_redpacket_rains')
    op.drop_index('ix_scheduled_rain_status', table_name='scheduled_redpacket_rains')
    op.drop_index('ix_scheduled_rain_start_time', table_name='scheduled_redpacket_rains')
    
    # 删除表
    op.drop_table('scheduled_redpacket_rains')

