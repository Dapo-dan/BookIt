"""create_all_tables_for_postgresql

Revision ID: 458ae2f144c4
Revises: 3be08a093053
Create Date: 2025-09-28 00:14:45.737808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '458ae2f144c4'
down_revision = '3be08a093053'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if we're using PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        # Skip this migration for non-PostgreSQL databases
        return
    
    # Create ENUM types for PostgreSQL
    booking_status_enum = sa.Enum('pending', 'confirmed', 'cancelled', 'completed', name='bookingstatus')
    user_role_enum = sa.Enum('user', 'admin', name='userrole')
    
    # Create the ENUM types (only if they don't exist)
    try:
        booking_status_enum.create(bind)
    except Exception:
        pass  # ENUM already exists
    
    try:
        user_role_enum.create(bind)
    except Exception:
        pass  # ENUM already exists
    
    # Check if tables already exist
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Create services table
    if 'services' not in existing_tables:
        op.create_table('services',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.String(length=2000), nullable=False),
            sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('duration_minutes', sa.Integer(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create users table
    if 'users' not in existing_tables:
        op.create_table('users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=120), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('role', user_role_enum, nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # Create bookings table
    if 'bookings' not in existing_tables:
        op.create_table('bookings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('service_id', sa.Integer(), nullable=False),
            sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
            sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
            sa.Column('status', booking_status_enum, nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create reviews table
    if 'reviews' not in existing_tables:
        op.create_table('reviews',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('booking_id', sa.Integer(), nullable=False),
            sa.Column('rating', sa.Integer(), nullable=False),
            sa.Column('comment', sa.String(length=2000), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('booking_id', name='uq_review_booking'),
            sa.CheckConstraint("rating >= 1 AND rating <= 5", name='ck_reviews_rating')
        )


def downgrade() -> None:
    # Check if we're using PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        # Skip this migration for non-PostgreSQL databases
        return
    
    # Check if tables exist before dropping
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Drop tables in reverse order
    if 'reviews' in existing_tables:
        op.drop_table('reviews')
    if 'bookings' in existing_tables:
        op.drop_table('bookings')
    if 'users' in existing_tables:
        op.drop_index(op.f('ix_users_id'), table_name='users')
        op.drop_index(op.f('ix_users_email'), table_name='users')
        op.drop_table('users')
    if 'services' in existing_tables:
        op.drop_table('services')
    
    # Drop ENUM types (only if they exist)
    try:
        sa.Enum(name='bookingstatus').drop(bind)
    except Exception:
        pass  # ENUM doesn't exist
    try:
        sa.Enum(name='userrole').drop(bind)
    except Exception:
        pass  # ENUM doesn't exist