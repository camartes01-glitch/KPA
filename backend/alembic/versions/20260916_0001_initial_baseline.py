"""initial_baseline

Revision ID: 0001_initial_baseline
Revises: 
Create Date: 2026-09-16 00:01:00.000000+05:30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. districts
    op.create_table(
        'districts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_kn', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_districts_name_en', 'districts', ['name_en'], unique=True)
    op.create_index('ix_districts_name_kn', 'districts', ['name_kn'], unique=False)
    op.create_index('ix_districts_code', 'districts', ['code'], unique=True)

    # 2. talukas
    op.create_table(
        'talukas',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('district_id', sa.Uuid(), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_kn', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_talukas_district_id', 'talukas', ['district_id'], unique=False)
    op.create_index('ix_talukas_name_en', 'talukas', ['name_en'], unique=False)
    op.create_index('ix_talukas_name_kn', 'talukas', ['name_kn'], unique=False)
    op.create_index('ix_talukas_code', 'talukas', ['code'], unique=False)

    # 3. users
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), server_default='MEMBER', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('district_id', sa.Uuid(), nullable=True),
        sa.Column('taluka_id', sa.Uuid(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_phone', 'users', ['phone'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)
    op.create_index('ix_users_status', 'users', ['status'], unique=False)
    op.create_index('ix_users_district_id', 'users', ['district_id'], unique=False)
    op.create_index('ix_users_taluka_id', 'users', ['taluka_id'], unique=False)

    # 4. device_sessions
    op.create_table(
        'device_sessions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=255), nullable=False),
        sa.Column('device_name', sa.String(length=100), nullable=True),
        sa.Column('device_id', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_device_sessions_user_id', 'device_sessions', ['user_id'], unique=False)
    op.create_index('ix_device_sessions_refresh_token_hash', 'device_sessions', ['refresh_token_hash'], unique=True)

    # 5. otp_verifications
    op.create_table(
        'otp_verifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('otp_code', sa.String(length=100), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('attempts', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('is_used', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_otp_verifications_phone', 'otp_verifications', ['phone'], unique=False)

    # 6. members
    op.create_table(
        'members',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('membership_no', sa.String(length=30), nullable=True),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('father_or_spouse_name', sa.String(length=150), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column('dob', sa.Date(), nullable=False),
        sa.Column('blood_group', sa.String(length=10), nullable=True),
        sa.Column('studio_name', sa.String(length=150), nullable=True),
        sa.Column('experience_years', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('photo_url', sa.Text(), nullable=True),
        sa.Column('id_card_qr_data', sa.Text(), nullable=True),
        sa.Column('address_line', sa.Text(), nullable=True),
        sa.Column('pincode', sa.String(length=10), nullable=True),
        sa.Column('district_id', sa.Uuid(), nullable=False),
        sa.Column('taluka_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('approved_by_id', sa.Uuid(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id']),
        sa.ForeignKeyConstraint(['taluka_id'], ['talukas.id']),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_members_user_id', 'members', ['user_id'], unique=True)
    op.create_index('ix_members_membership_no', 'members', ['membership_no'], unique=True)
    op.create_index('ix_members_full_name', 'members', ['full_name'], unique=False)
    op.create_index('ix_members_district_id', 'members', ['district_id'], unique=False)
    op.create_index('ix_members_taluka_id', 'members', ['taluka_id'], unique=False)
    op.create_index('ix_members_status', 'members', ['status'], unique=False)

    # 7. nominees
    op.create_table(
        'nominees',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('member_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('relationship_to_member', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('dob', sa.Date(), nullable=True),
        sa.Column('aadhaar_last_4', sa.String(length=4), nullable=True),
        sa.Column('bank_account_no', sa.String(length=50), nullable=True),
        sa.Column('bank_ifsc', sa.String(length=20), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('is_primary', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_nominees_member_id', 'nominees', ['member_id'], unique=False)

    # 8. welfare_events
    op.create_table(
        'welfare_events',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('deceased_member_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('death_date', sa.Date(), nullable=False),
        sa.Column('cause_of_death', sa.Text(), nullable=True),
        sa.Column('death_certificate_url', sa.Text(), nullable=True),
        sa.Column('target_amount', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False),
        sa.Column('collected_amount', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='ACTIVE', nullable=False),
        sa.Column('created_by_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['deceased_member_id'], ['members.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_welfare_events_deceased_member_id', 'welfare_events', ['deceased_member_id'], unique=False)
    op.create_index('ix_welfare_events_status', 'welfare_events', ['status'], unique=False)

    # 9. welfare_contributions
    op.create_table(
        'welfare_contributions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('event_id', sa.Uuid(), nullable=False),
        sa.Column('member_id', sa.Uuid(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=8, scale=2), server_default=sa.text('10.00'), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('payment_method', sa.String(length=30), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['welfare_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'member_id', name='uq_welfare_event_member'),
    )
    op.create_index('ix_welfare_contributions_event_id', 'welfare_contributions', ['event_id'], unique=False)
    op.create_index('ix_welfare_contributions_member_id', 'welfare_contributions', ['member_id'], unique=False)
    op.create_index('ix_welfare_contributions_status', 'welfare_contributions', ['status'], unique=False)

    # 10. payments
    op.create_table(
        'payments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('contribution_id', sa.Uuid(), nullable=True),
        sa.Column('member_id', sa.Uuid(), nullable=False),
        sa.Column('gateway', sa.String(length=20), server_default='RAZORPAY', nullable=False),
        sa.Column('gateway_order_id', sa.String(length=100), nullable=False),
        sa.Column('gateway_payment_id', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=5), server_default='INR', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='CREATED', nullable=False),
        sa.Column('payment_method', sa.String(length=30), nullable=True),
        sa.Column('receipt_no', sa.String(length=50), nullable=False),
        sa.Column('signature', sa.String(length=255), nullable=True),
        sa.Column('raw_payload', sa.Text(), nullable=True),
        sa.Column('error_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['contribution_id'], ['welfare_contributions.id']),
        sa.ForeignKeyConstraint(['member_id'], ['members.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_payments_contribution_id', 'payments', ['contribution_id'], unique=False)
    op.create_index('ix_payments_member_id', 'payments', ['member_id'], unique=False)
    op.create_index('ix_payments_gateway_order_id', 'payments', ['gateway_order_id'], unique=True)
    op.create_index('ix_payments_gateway_payment_id', 'payments', ['gateway_payment_id'], unique=True)
    op.create_index('ix_payments_receipt_no', 'payments', ['receipt_no'], unique=True)
    op.create_index('ix_payments_status', 'payments', ['status'], unique=False)

    # 11. autopay_mandates
    op.create_table(
        'autopay_mandates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('member_id', sa.Uuid(), nullable=False),
        sa.Column('gateway', sa.String(length=20), server_default='RAZORPAY', nullable=False),
        sa.Column('gateway_mandate_id', sa.String(length=100), nullable=False),
        sa.Column('auth_type', sa.String(length=50), server_default='UPI', nullable=False),
        sa.Column('max_amount', sa.Numeric(precision=8, scale=2), server_default=sa.text('500.00'), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='CREATED', nullable=False),
        sa.Column('vpa', sa.String(length=100), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('bank_account_last_4', sa.String(length=4), nullable=True),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_autopay_mandates_member_id', 'autopay_mandates', ['member_id'], unique=False)
    op.create_index('ix_autopay_mandates_gateway_mandate_id', 'autopay_mandates', ['gateway_mandate_id'], unique=True)
    op.create_index('ix_autopay_mandates_status', 'autopay_mandates', ['status'], unique=False)

    # 12. notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('district_id', sa.Uuid(), nullable=True),
        sa.Column('taluka_id', sa.Uuid(), nullable=True),
        sa.Column('channel', sa.String(length=50), server_default='IN_APP', nullable=False),
        sa.Column('type', sa.String(length=50), server_default='GENERAL_BROADCAST', nullable=False),
        sa.Column('title_en', sa.String(length=255), nullable=False),
        sa.Column('title_kn', sa.String(length=255), nullable=False),
        sa.Column('body_en', sa.Text(), nullable=False),
        sa.Column('body_kn', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['district_id'], ['districts.id']),
        sa.ForeignKeyConstraint(['taluka_id'], ['talukas.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'], unique=False)
    op.create_index('ix_notifications_district_id', 'notifications', ['district_id'], unique=False)
    op.create_index('ix_notifications_taluka_id', 'notifications', ['taluka_id'], unique=False)

    # 13. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('payload_json', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'], unique=False)
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'], unique=False)
    op.create_index('ix_audit_logs_resource_id', 'audit_logs', ['resource_id'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('notifications')
    op.drop_table('autopay_mandates')
    op.drop_table('payments')
    op.drop_table('welfare_contributions')
    op.drop_table('welfare_events')
    op.drop_table('nominees')
    op.drop_table('members')
    op.drop_table('otp_verifications')
    op.drop_table('device_sessions')
    op.drop_table('users')
    op.drop_table('talukas')
    op.drop_table('districts')
