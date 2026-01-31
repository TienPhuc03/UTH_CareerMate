from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'eb5428c0c5de'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables from scratch"""
    
    # ========== CREATE USERS TABLE ==========
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('role', sa.String(length=50), server_default='candidate', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])
    
    # ========== CREATE JOBS TABLE ==========
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('benefits', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('is_approved', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('recruiter_id', sa.Integer(), nullable=True),
        sa.Column('recruiter_email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['recruiter_id'], ['users.id'], name='fk_jobs_recruiter_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_jobs_id', 'jobs', ['id'])
    op.create_index('ix_jobs_title', 'jobs', ['title'])
    op.create_index('ix_jobs_recruiter_id', 'jobs', ['recruiter_id'])
    op.create_index('ix_jobs_recruiter_email', 'jobs', ['recruiter_email'])
    
    # ========== CREATE CVS TABLE ==========
    op.create_table(
        'cvs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.Column('experience', sa.Text(), nullable=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_type', sa.String(length=10), nullable=True),
        sa.Column('ats_score', sa.Float(), nullable=True),
        sa.Column('ai_feedback', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_cvs_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cvs_id', 'cvs', ['id'])
    op.create_index('ix_cvs_user_id', 'cvs', ['user_id'])
    
    # ========== CREATE APPLICATIONS TABLE ==========
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('cv_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), server_default='PENDING', nullable=True),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('matching_score', sa.Float(), nullable=True),
        sa.Column('matched_skills', sa.Text(), nullable=True),
        sa.Column('missing_skills', sa.Text(), nullable=True),
        sa.Column('recruiter_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['cv_id'], ['cvs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_applications_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_applications_id', 'applications', ['id'])
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])
    
    # ========== CREATE AI_COACH_FEEDBACKS TABLE ==========
    op.create_table(
        'ai_coach_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('matching_score', sa.Float(), nullable=True),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('suggested_skills', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_coach_feedbacks_id', 'ai_coach_feedbacks', ['id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('ai_coach_feedbacks')
    op.drop_table('applications')
    op.drop_table('cvs')
    op.drop_table('jobs')
    op.drop_table('users')