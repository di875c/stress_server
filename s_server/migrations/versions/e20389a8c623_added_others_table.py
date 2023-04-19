"""added_others_table

Revision ID: e20389a8c623
Revises: caca3593fc24
Create Date: 2023-04-19 18:36:06.781689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e20389a8c623'
down_revision = 'caca3593fc24'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cs',
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('time_created', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('time_updated', sa.TIMESTAMP(), nullable=True),
    sa.Column('coord_x', sa.Float(), nullable=False),
    sa.Column('coord_y', sa.Float(), nullable=False),
    sa.Column('coord_z', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_table('other',
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('time_created', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('time_updated', sa.TIMESTAMP(), nullable=True),
    sa.Column('card_str', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_unique_constraint(None, 'base_structure', ['name'])
    op.create_unique_constraint(None, 'frame', ['number'])
    op.add_column('node', sa.Column('cs', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'node', 'cs', ['cs'], ['uid'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'node', type_='foreignkey')
    op.drop_column('node', 'cs')
    op.drop_constraint(None, 'frame', type_='unique')
    op.drop_constraint(None, 'base_structure', type_='unique')
    op.drop_table('other')
    op.drop_table('cs')
    # ### end Alembic commands ###
