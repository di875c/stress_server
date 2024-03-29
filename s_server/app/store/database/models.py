from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
import os, dotenv
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




DB = {
        'drivername': os.environ.get('POSTGRES_ENGINE'),
        'database': os.environ.get('POSTGRES_DB'),
        'username': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'url': os.environ.get('POSTGRES_URL')
}

PG_DATABASE = f"{DB['drivername']}://{DB['username']}:{DB['password']}@{DB['url']}/{DB['database']}"

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
    uid = Column('uid', Integer, nullable=False, primary_key=True)
    type = Column(String)
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


class CoordSys(BaseICom, XYZMixin):
    __tablename__ = 'cs'


class SectionPropertyMap(Base):
    __tablename__ = 'SectionPropertyMap'
    frame = Column('frame', Integer, ForeignKey('frame.number', ondelete="CASCADE",
                                    onupdate="CASCADE"), nullable=False, primary_key=True)
    uid = Column('uid', Integer, ForeignKey('section_property.uid', ondelete="CASCADE",
                                                                  onupdate="CASCADE"), primary_key=True)
    stringer = Column('stringer', Integer, nullable=False, primary_key=True)
    side = Column('side', String(3), nullable=False, primary_key=True)
    __table_args__ = (ForeignKeyConstraint(['stringer', 'side'], ['stringer.number', 'stringer.side'],
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


class SectionProperty(BaseICom, XYZMixin):
    __tablename__ = 'section_property'
    geo_type = Column('Ref_Geometry', String, ForeignKey('base_structure.name'))
    area = Column('A', Float())
    inertia_zz = Column('I1', Float())
    inertia_yy = Column('I2', Float())
    inertia_yz = Column('I12', Float())
    inertia_torsion = Column('J', Float())
    alpha = Column(Float())
    inertia_min = Column('Imin', Float())
    inertia_max = Column('Imax', Float())
    positions = relationship("SectionPropertyMap", lazy='selectin')


class Section(BaseICom, XYZMixin, ReferenceMixin):
    __tablename__ = 'sections'
    geo_type = Column('Ref_Geometry', String, ForeignKey('base_structure.name'))
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


# class NodeRBE(Base):
#     __tablename__ = 'NodeElement'
#     node = Column('node', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
#     rbe = Column('rbe', Integer, ForeignKey('rbe.uid', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)


class Node(ReferenceMixin, BaseICom, XYZMixin):
    __tablename__ = 'node'
    cs = Column('cs', Integer, ForeignKey('cs.uid'))
    # elements = relationship('Element', secondary=NodeElement.__table__, back_populates="nodes", lazy='selectin')


class Element(BaseICom):
    __tablename__ = 'element'
    # nodes = relationship('Node', secondary=NodeElement.__table__, back_populates="elements", lazy='selectin')
    element_ref = Column('base_structure', String, ForeignKey('base_structure.name'), nullable=False) #foreign key to element type
    property_id = Column('pid', Integer, ForeignKey('property.uid'))
    node_1 = Column('node_1', Integer, ForeignKey('node.uid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
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
    __tablename__ = 'property'
    material_id = Column('material', Integer, ForeignKey('material.uid'))
    shell_thick = Column('shell_thick', Float)
    section_start = Column('start_property', Integer, ForeignKey('section_property.uid'))
    section_end = Column('end_property', Integer, ForeignKey('section_property.uid'))
    property_start = relationship("SectionProperty", lazy='selectin', uselist=False,
                                  foreign_keys=[section_start])
    property_end = relationship("SectionProperty", lazy='selectin', uselist=False,
                                foreign_keys=[section_end])


# class RBE(BaseICom):
#     __tablename__ = 'rbe'
#     node = Column('node', Integer, ForeignKey('node.uid'))
#     nodes = relationship('Node', secondary=Node.__table__, back_populates="rbe", lazy='selectin')


class Others(BaseICom):
    __tablename__ = 'other'
    card_str = Column(String)
