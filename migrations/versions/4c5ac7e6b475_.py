"""empty message

Revision ID: 4c5ac7e6b475
Revises: 94ab44d6b46b
Create Date: 2020-11-17 20:21:49.846827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c5ac7e6b475'
down_revision = '94ab44d6b46b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('person', sa.Column('mobile_number', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('person', 'mobile_number')
    # ### end Alembic commands ###
