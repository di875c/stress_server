from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, relationship, declarative_mixin, declared_attr
from sqlalchemy import (
    Column,
    Identity,
    String,
    Integer,
    Float,
    DateTime,
    TIMESTAMP,
    Table,
    Computed,
    ForeignKey,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    func
)
# from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

DATABASE = {
        'drivername': os.environ.get('POSTGRES_ENGINE', 'postgresql+asyncpg'),
        'database': os.environ.get('POSTGRES_DB', 'stress_postgres'),
        'username': os.environ.get('POSTGRES_USER', 'stress_user'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'stress_1234!'),
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432')
}
PG_DATABASE = 'postgresql+asyncpg://stress_user:stress_1234!@localhost/stress_postgres'
# создаем движок
engine = create_async_engine(PG_DATABASE, echo=True)
# создаем метод описания БД (Создаем базовый класс для декларативных определений классов.)
Base = declarative_base()
# создаем сессию (Фабрика sessionmaker генерирует новые объекты Session при вызове)
Session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class BaseICom(Base):
    __abstract__ = True
    uid = Column(Integer, Identity(start=1, cycle=True), unique=True, primary_key=True)
    comment = Column('comment', String())
    time_created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    time_updated = Column(TIMESTAMP, onupdate=func.now())

@declarative_mixin
class XYZMixin:
    __abstract__ = True
    cog_x = Column(Float(), nullable=False)
    cog_y = Column(Float(), nullable=False)
    cog_z = Column(Float(), nullable=False)

@declarative_mixin
class ReferenceMixin:
    __abstract__ = True
    @declared_attr
    def frame(cls):
        return Column('frame', Integer, ForeignKey('frame.number', ondelete="CASCADE",
                                                           onupdate="CASCADE"), nullable=False)
    stringer = Column('stringer', Integer, nullable=False)
    side = Column('side', String(3), nullable=False)
    @declared_attr
    def __table_args__(cls):
        return (ForeignKeyConstraint(['stringer', 'side'], ['stringer.number', 'stringer.side'],
                                           name='stringer_reference'), {})


class BaseStructure(Base):
    __tablename__ = 'base_structure'
    name = Column('name', String(20), unique=True, nullable=False, primary_key=True)


class Frame(Base):
    __tablename__ = 'frame'
    number = Column('number',  Integer, unique=True, nullable=False, primary_key=True)


class Stringer(Base):
    __tablename__ = 'stringer'
    number = Column('number', Integer, nullable=False)
    side = Column('side', String(3), nullable=False)
    reference = PrimaryKeyConstraint(number, side, name='stringer_reference')


class Structure(Base):
    __tablename__ = 'structure_table'
    struct_type = Column('struct_type', ForeignKey('base_structure.name'), nullable=False)
    number = Column('number', Float(precision=1), nullable=False)
    side = Column('side', String(3), nullable=True)
    reference = PrimaryKeyConstraint(struct_type, number, side, name='unique_reference')
    #
    # @hybrid_property
    # def reference_add(self):
    #     return self.struct_type + self.number


class SectionProperty(BaseICom, XYZMixin, ReferenceMixin):
    __tablename__ = 'section_property'
    type = Column('type', String(), ForeignKey('base_structure.name'))
    area = Column(Float())
    inertia_xx = Column(Float())
    inertia_yy = Column(Float())
    inertia_zz = Column(Float())


class Material(BaseICom):
    __tablename__ = 'material'
    density = Column(Float())
    eu = Column(Float(), nullable=False)
    nu = Column(Float(), nullable=False)
    properties = relationship("ElProperty", lazy="selectin")


class Mass(BaseICom, XYZMixin, ReferenceMixin):
    __tablename__ = 'mass'
    name = Column(String, nullable=False)
    weight = Column(Float())


class NodeElement(Base):
    __tablename__ = 'NodeElement'
    node = Column('node', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    element = Column('element', Integer, ForeignKey('element.uid', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)


class Node(ReferenceMixin, BaseICom, XYZMixin, ):
    __tablename__ = 'node'
    # reference_type1 = Column('reference_type1', String(20), nullable=False)
    # reference_number1 = Column('reference_number1', Float(precision=1), nullable=False)
    # reference_side1 = Column('reference_side1', String(3), nullable=True)
    # __table_args__ = (ForeignKeyConstraint(['reference_type1', 'reference_number1', 'reference_side1'],
    #                                        ['structure_table.struct_type', 'structure_table.number',
    #                                         'structure_table.side'], name='reference_1'), {})
    # reference_type2 = Column('reference_type2', String(20), nullable=False)
    # reference_number2 = Column('reference_number2', Float(precision=1), nullable=False)
    # reference_side2 = Column('reference_side2', String(3), nullable=True)
    # __table_args__ = (ForeignKeyConstraint(['reference_type2', 'reference_number2', 'reference_side2'],
    #                                        ['structure_table.struct_type', 'structure_table.number',
    #                                         'structure_table.side'], name='reference_2'), {})
    # frame = Column('frame', Float(precision=1), ForeignKey('frame.number', ondelete="CASCADE",
    #                                                               onupdate="CASCADE"), nullable=False)
    # stringer = Column('stringer', Float(precision=1), nullable=False)
    # side = Column('side', String(3), nullable=False)
    # __table_args__ = (ForeignKeyConstraint(['stringer', 'side'], ['stringer.number', 'stringer.side'],
    #                                        name='stringer_reference'), {})
    elements = relationship('Element', secondary=NodeElement.__table__, back_populates="nodes", lazy='selectin')


class Element(BaseICom):
    __tablename__ = 'element'
    nodes = relationship('Node', secondary=NodeElement.__table__, back_populates="elements", lazy='selectin')
    element_type = Column('base_structure', String, ForeignKey('base_structure.name'), nullable=False) #foreign key to element type
    property_id = Column('property', Integer, ForeignKey('property.uid'))
    offset = Column(String)
    node_start = Column('node_start', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"))
    node_end = Column('node_end', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"))
    property_start = Column('property_start', Integer, ForeignKey('property.uid'))
    property_end = Column('property_end', Integer, ForeignKey('property.uid'))
    position = relationship('Node', back_populates="elements", lazy='selectin', uselist=False, foreign_keys=[node_start])


class ElProperty(BaseICom):
    """
    TODO: COG to be concidered, what point has to be used?
    """
    __tablename__ = 'property'
    cross_section = Column('cross_section', Integer, ForeignKey('section_property.uid'))
    shell_thick = Column('shell_thick', Float)
    material_id = Column('material', Integer, ForeignKey('material.uid'))
    material = relationship("Material", lazy='selectin')
    section = relationship("SectionProperty", lazy='selectin')
