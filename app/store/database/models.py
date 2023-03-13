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
    coord_x = Column(Float(), nullable=False)
    coord_y = Column(Float(), nullable=False)
    coord_z = Column(Float(), nullable=False)


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


class SectionProperty(BaseICom, XYZMixin, ReferenceMixin):
    __tablename__ = 'section_property'
    type = Column('type', String(), ForeignKey('base_structure.name'))
    area = Column('A', Float())
    inertia_xx = Column('I1', Float())
    inertia_yy = Column('I2', Float())
    inertia_xy = Column('I12', Float())
    inertia_torsion = Column('J', Float())
    alpha = Column(Float())
    inertia_min = Column('Imin', Float())
    inertia_max = Column('Imax', Float())


class Section(BaseICom, XYZMixin, ReferenceMixin):
    __tablename__ = 'sections'
    type = Column(String(), nullable=False)
    section_type = Column(String(), nullable=False)
    height = Column(Float())
    width_1 = Column(Float(), nullable=False)
    th_1 = Column(Float())
    width_2 = Column(Float())
    th_2 = Column(Float())
    width_3 = Column(Float())
    th_3 = Column(Float())
    width_4 = Column(Float())
    th_4 = Column(Float())
    alpha = Column(Float(), nullable=False)


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


# class NodeElement(Base):
#     __tablename__ = 'NodeElement'
#     node = Column('node', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
#     element = Column('element', Integer, ForeignKey('element.uid', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)


class Node(ReferenceMixin, BaseICom, XYZMixin, ):
    __tablename__ = 'node'
    # elements = relationship('Element', secondary=NodeElement.__table__, back_populates="nodes", lazy='selectin')


class Element(BaseICom):
    __tablename__ = 'element'
    # nodes = relationship('Node', secondary=NodeElement.__table__, back_populates="elements", lazy='selectin')
    element_type = Column('base_structure', String, ForeignKey('base_structure.name'), nullable=False) #foreign key to element type
    property_id = Column('pid', Integer, ForeignKey('property.uid'))
    offset_start = Column(Float)
    offset_end = Column(Float)
    node_1 = Column('node_1', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"))
    node_2 = Column('node_2', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"))
    node_3 = Column('node_3', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"))
    node_4 = Column('node_4', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"))
    position = relationship('Node', lazy='selectin', uselist=False, foreign_keys=[node_1])
    off_1_x = Column(Float)
    off_1_y = Column(Float)
    off_1_z = Column(Float)
    off_2_x = Column(Float)
    off_2_y = Column(Float)
    off_2_z = Column(Float)

    @hybrid_property
    def offset_1(self):
        if None in (self.off_1_x, self.off_1_y, self.off_1_z):
            return None
        return f"<{self.off_1_x} {self.off_1_y} {self.off_1_z}>"

    @offset_1.setter
    def offset_1(self, offset_1):
        self.off_1_x, self.off_1_y, self.off_1_z = [float(x) for x in offset_1[1:-1].split()]

    @hybrid_property
    def offset_2(self):
        if None in (self.off_2_x, self.off_2_y, self.off_2_z):
            return None
        return f"<{self.off_2_x} {self.off_2_y} {self.off_2_z}>"

    @offset_2.setter
    def offset_2(self, offset_2):
        self.off_2_x, self.off_2_y, self.off_2_z = [float(x) for x in offset_2[1:-1].split()]

class ElProperty(BaseICom):
    """
    TODO: COG to be concidered, what point has to be used?
    """
    __tablename__ = 'property'
    property_type = Column('type', String)
    material_id = Column('material', Integer, ForeignKey('material.uid'))
    shell_thick = Column('shell_thick', Float)
    section_start = Column('start_property', Integer, ForeignKey('section_property.uid'))
    section_end = Column('end_property', Integer, ForeignKey('section_property.uid'))
    property_start = relationship("SectionProperty", lazy='selectin', uselist=False,
                                  foreign_keys=[section_start])
    property_end = relationship("SectionProperty", lazy='selectin', uselist=False,
                                foreign_keys=[section_end])
