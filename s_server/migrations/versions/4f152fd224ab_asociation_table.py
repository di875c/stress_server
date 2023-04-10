"""Asociation table

Revision ID: 4f152fd224ab
Revises: a9485f675323
Create Date: 2023-03-21 14:03:49.069994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f152fd224ab'
down_revision = 'a9485f675323'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('SectionPropertyReference',
    sa.Column('frame', sa.Integer(), nullable=False),
    sa.Column('sec_prop_uid', sa.Integer(), nullable=False),
    sa.Column('stringer', sa.Integer(), nullable=False),
    sa.Column('side', sa.String(length=3), nullable=False),
    sa.ForeignKeyConstraint(['frame'], ['frame.number'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sec_prop_uid'], ['section_property.uid'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['stringer', 'side'], ['stringer.number', 'stringer.side'], name='stringer_reference'),
    sa.PrimaryKeyConstraint('frame', 'sec_prop_uid', 'stringer', 'side')
    )
    op.drop_constraint('section_property_frame_fkey', 'section_property', type_='foreignkey')
    op.drop_constraint('stringer_reference', 'section_property', type_='foreignkey')
    op.drop_column('section_property', 'frame')
    op.drop_column('section_property', 'stringer')
    op.drop_column('section_property', 'side')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('section_property', sa.Column('side', sa.VARCHAR(length=3), autoincrement=False, nullable=True))
    op.add_column('section_property', sa.Column('stringer', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('section_property', sa.Column('frame', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('stringer_reference', 'section_property', 'stringer', ['stringer', 'side'], ['number', 'side'])
    op.create_foreign_key('section_property_frame_fkey', 'section_property', 'frame', ['frame'], ['number'], onupdate='CASCADE', ondelete='CASCADE')
    op.drop_table('SectionPropertyReference')
    # ### end Alembic commands ###