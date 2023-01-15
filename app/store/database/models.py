from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import (
    Column,
    Identity,
    String,
    Integer,
    Float,
    Table,
    Computed,
    ForeignKey,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    func
)
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
# association_table = Table(
#     "association_table",
#     Base.metadata,
#     Column("structure_table", ForeignKey("structure_table.id")),
#     Column("mass_table", ForeignKey("mass_table.id")),
# )

class BaseICom(Base):
    __abstract__ = True
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    comment = Column('comment', String())

class BaseCOG(Base):
    __abstract__ = True
    cog_x = Column(Float(), nullable=False)
    cog_y = Column(Float(), nullable=False)
    cog_z = Column(Float(), nullable=False)

class BaseStructure(Base):
    __tablename__ = 'base_structure'
    name = Column('name', String(20), unique=True, nullable=False, primary_key=True)

#
# class ElementType(BaseStructure):
#     __tablename__ = 'element_type'
    # name = Column('name', String(20), unique=True, nullable=False, primary_key=True)

class Structure(BaseICom):
    __tablename__ = 'structure_table'
    struct_type = Column('struct_type', ForeignKey('base_structure.name'), nullable=False)
    number = Column('number', Float(precision=1), nullable=False)
    side = Column('side', String(3), nullable=True)
    reference = PrimaryKeyConstraint(struct_type, number, side, name='unique_reference')
    #
    # @hybrid_property
    # def reference_add(self):
    #     return self.struct_type + self.number


class SectionProperty(BaseICom, BaseCOG):
    __tablename__ = 'section_property'
    # name_id = Column('name_id', Integer, nullable=False, unique=True)
    reference_type = Column('reference_type', String(20), nullable=False)
    reference_number = Column('reference_number', Float(precision=1), nullable=False)
    side = Column('side', String(3), nullable=True)
    __table_args__ = (ForeignKeyConstraint(['reference_type', 'reference_number', 'side'],
        ['structure_table.struct_type', 'structure_table.number', 'structure_table.side'], name='reference'), {})
    position_type = Column('position_type', String(20), nullable=False)
    position_number = Column('position_number', Float(precision=1), nullable=False)
    position_side = Column('position_side', String(3), nullable=True)
    __table_args__ = (ForeignKeyConstraint(['position_type', 'position_number', 'position_side'],
                                           ['structure_table.struct_type', 'structure_table.number', 'structure_table.side'],
                                           name='position'), {})
    area = Column(Float())
    inertia_xx = Column(Float())
    inertia_yy = Column(Float())
    inertia_zz = Column(Float())


class Material(BaseICom):
    __tablename__ = 'material_table'
    # name_id = Column(Integer, nullable=False, unique=True)
    density = Column(Float())
    eu = Column(Float(), nullable=False)
    nu = Column(Float(), nullable=False)


class Mass(BaseICom, BaseCOG):
    __tablename__ = 'mass_table'
    name = Column(String, nullable=False)
    weight = Column(Float())
    reference_type = Column('reference_type', String(20), nullable=False)
    reference_number = Column('reference_number', Float(precision=1), nullable=False)
    side = Column('side', String(3), nullable=True)
    __table_args__ = (ForeignKeyConstraint(['reference_type', 'reference_number', 'side'],
                                           ['structure_table.struct_type', 'structure_table.number',
                                            'structure_table.side'], name='reference'), {})


class NodeElement(Base):
    __tablename__ = 'NodeElement'
    # id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    node = Column('node', Integer, ForeignKey('node.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    element = Column('element', Integer, ForeignKey('element.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)


class Node(BaseICom, BaseCOG):
    __tablename__ = 'node'
    # node_id = Column('node_id', Integer, nullable=False, unique=True)
    reference_type1 = Column('reference_type1', String(20), nullable=False)
    reference_number1 = Column('reference_number1', Float(precision=1), nullable=False)
    reference_side1 = Column('reference_side1', String(3), nullable=True)
    __table_args__ = (ForeignKeyConstraint(['reference_type1', 'reference_number1', 'reference_side1'],
                                           ['structure_table.struct_type', 'structure_table.number',
                                            'structure_table.side'], name='reference_1'), {})
    reference_type2 = Column('reference_type2', String(20), nullable=False)
    reference_number2 = Column('reference_number2', Float(precision=1), nullable=False)
    reference_side2 = Column('reference_side2', String(3), nullable=True)
    __table_args__ = (ForeignKeyConstraint(['reference_type2', 'reference_number2', 'reference_side2'],
                                           ['structure_table.struct_type', 'structure_table.number',
                                            'structure_table.side'], name='reference_2'), {})
    elements = relationship('Element', secondary=NodeElement.__table__, back_populates="nodes", lazy='selectin')


class Element(BaseICom):
    __tablename__ = 'element'
    # element_id = Column('element_id', Integer, nullable=False, unique=True)
    element_type = Column('base_structure', String, ForeignKey('base_structure.name'), nullable=False) #foreign key to element type
    nodes = relationship('Node', secondary=NodeElement.__table__, back_populates="elements", lazy='selectin')
    property_id = Column('property', Integer, ForeignKey('property.id'))
    offset = Column(String)


class ElProperty(BaseICom, BaseCOG):
    """
    TODO: COG to be concidered, what point has to be used?
    """
    __tablename__ = 'property'
    # name_id = Column('property_id', Integer, nullable=False, unique=True)
    cross_section = Column('cross-section', Integer, ForeignKey('section_property.id'))
