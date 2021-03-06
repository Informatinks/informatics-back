"""empty message

Revision ID: c1ba34f5e083
Revises: a6a54a1a8e5b
Create Date: 2019-05-16 17:33:03.779094

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c1ba34f5e083'
down_revision = 'a6a54a1a8e5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contest_monitor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workshop_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.Column('user_visibility', sa.Integer(), nullable=False),
    sa.Column('with_penalty_time', sa.Boolean(), nullable=True),
    sa.Column('freeze_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['workshop_id'], ['pynformatics.workshop.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='pynformatics'
    )
    op.alter_column('workshop_connection', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('workshop_connection', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_table('contest_monitor', schema='pynformatics')
    # ### end Alembic commands ###
