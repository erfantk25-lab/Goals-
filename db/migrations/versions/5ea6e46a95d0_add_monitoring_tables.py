"""Add monitoring tables

Revision ID: 5ea6e46a95d0
Revises: 
Create Date: 2026-06-25 21:07:20.971188

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ea6e46a95d0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('model_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('metric_name', sa.String(), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_metrics_id'), 'model_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_model_metrics_metric_name'), 'model_metrics', ['metric_name'], unique=False)
    op.create_index(op.f('ix_model_metrics_timestamp'), 'model_metrics', ['timestamp'], unique=False)

    op.create_table('llm_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('prompt_version_id', sa.String(), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False),
        sa.Column('output_tokens', sa.Integer(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('validation_success', sa.Boolean(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_llm_metrics_id'), 'llm_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_llm_metrics_timestamp'), 'llm_metrics', ['timestamp'], unique=False)

    op.create_table('system_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('request_id', sa.String(), nullable=False),
        sa.Column('endpoint', sa.String(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('request_payload', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_logs_id'), 'system_logs', ['id'], unique=False)
    op.create_index(op.f('ix_system_logs_request_id'), 'system_logs', ['request_id'], unique=False)
    op.create_index(op.f('ix_system_logs_timestamp'), 'system_logs', ['timestamp'], unique=False)

    op.create_table('drift_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('drift_score', sa.Float(), nullable=False),
        sa.Column('drift_detected', sa.Boolean(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('feature_name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_drift_metrics_id'), 'drift_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_drift_metrics_timestamp'), 'drift_metrics', ['timestamp'], unique=False)

    op.create_table('alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('alert_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_alert_type'), 'alerts', ['alert_type'], unique=False)
    op.create_index(op.f('ix_alerts_timestamp'), 'alerts', ['timestamp'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('alerts')
    op.drop_table('drift_metrics')
    op.drop_table('system_logs')
    op.drop_table('llm_metrics')
    op.drop_table('model_metrics')
