"""Initial migration.

Revision ID: 71a4e563141f
Revises: dbca41014dde
Create Date: 2022-11-12 00:40:27.928741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71a4e563141f'
down_revision = 'dbca41014dde'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
