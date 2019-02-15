"""initial

Revision ID: f04e1b482733
Revises:
Create Date: 2019-01-27 17:03:13.780816

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f04e1b482733'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('_job', sa.Column('job_id', sa.Integer(), nullable=False),
                    sa.Column('url', sa.String(), nullable=True),
                    sa.Column('periodicity', sa.Integer()),
                    sa.PrimaryKeyConstraint('job_id'),
                    sa.UniqueConstraint('url'))
    op.create_table(
        'video', sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('video_url', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('duration', sa.String(), nullable=False),
        sa.Column('views', sa.String(), nullable=False),
        sa.Column('thumbnail_image', sa.String(), nullable=False),
        sa.Column('original_full_sized_image', sa.String(), nullable=False),
        sa.Column('local_thumbnail_image', sa.String(), nullable=True),
        sa.Column(
            'local_original_full_sized_image', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['_job.job_id'],
                                ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('video_id'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('video')
    op.drop_table('_job')
    # ### end Alembic commands ###