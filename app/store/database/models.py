from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import (
    Column,
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
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    comment = Column('comment', String())

class BaseCOG(Base):
    __abstract__ = True
    cog_x = Column(Float(), nullable=False)
    cog_y = Column(Float(), nullable=False)
    cog_z = Column(Float(), nullable=False)

class BaseStructure(Base):
    __tablename__ = 'base_structure'
    name = Column('name', String(20), unique=True, nullable=False, primary_key=True)


class ElementType(BaseStructure):
    __tablename__ = 'base_structure'
    # name = Column('name', String(20), unique=True, nullable=False, primary_key=True)

class Structure(BaseICom):
    __tablename__ = 'structure_table'
    id = Column(Integer, autoincrement=True)
    struct_type = Column('struct_type', ForeignKey('base_structure.name'), nullable=False)
    number = Column('number', Float(precision=1), nullable=False)
    side = Column('side', String(3), nullable=True)
    reference = PrimaryKeyConstraint(struct_type, number, side, name='unique_reference')

    @hybrid_property
    def reference_add(self):
        return self.struct_type + self.number


class SectionProperty(BaseICom, BaseCOG):
    __tablename__ = 'section_property'
    name = Column(String)
    reference_type = Column('reference_type', String(20), nullable=False)
    reference_number = Column('reference_number', Float(precision=1), nullable=False)
    __table_args__ = (ForeignKeyConstraint(['reference_type', 'reference_number'],
        ['structure_table.struct_type', 'structure_table.number'], name='reference'), {})
    position_type = Column('reference_type', String(20), nullable=False)
    Position_number = Column('reference_number', Float(precision=1), nullable=False)
    __table_args__ = (ForeignKeyConstraint(['position_type', 'position_number'],
                                           ['structure_table.struct_type', 'structure_table.number'],
                                           name='position'), {})
    area = Column(Float())
    inertia_xx = Column(Float())
    inertia_yy = Column(Float())
    inertia_zz = Column(Float())


class Material(BaseICom):
    __tablename__ = 'material_table'
    name_id = Column(Integer, nullable=False, unique=True)
    density = Column(Float())
    eu = Column(Float(), nullable=False)
    nu = Column(Float(), nullable=False)


class Mass(BaseICom, BaseCOG):
    __tablename__ = 'mass_table'
    name = Column(String, nullable=False)
    weight = Column(Float())
    reference_type = Column('reference_type', String(20), nullable=False)
    reference_number = Column('reference_number', Float(precision=1), nullable=False)
    __table_args__ = (ForeignKeyConstraint(['reference_type', 'reference_number'],
        ['structure_table.struct_type', 'structure_table.number'], name='reference_1'), {})


class NodeElement(Base):
    __tablename__ = 'NodeElement5'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    node = Column('nodeID', Integer, ForeignKey('Node.node_id'))
    element = Column('elementID', Integer, ForeignKey('Element.element_id'))


class Node(BaseICom, BaseCOG):
    __tablename__ = 'Node'
    name_id = Column(Integer, nullable=False, unique=True)
    reference_type1 = Column('reference_type1', String(20), nullable=False)
    reference_number1 = Column('reference_number1', Float(precision=1), nullable=False)
    __table_args__ = (ForeignKeyConstraint(['reference_type1', 'reference_number1'],
                                           ['structure_table.struct_type', 'structure_table.number'],
                                           name='reference_1'), {})
    reference_type2 = Column('reference_type2', String(20), nullable=False)
    reference_number2 = Column('reference_number2', Float(precision=1), nullable=False)
    reference_side = Column('reference_side', String(20), nullable=True)
    __table_args__ = (ForeignKeyConstraint(['reference_type2', 'reference_number2', 'reference_side'],
                                           ['structure_table.struct_type', 'structure_table.number', 'structure_table.side'],
                                               name='reference_2'), {})
    elements = relationship('Element', secondary=NodeElement.__table__, backref='Node')


class Element(BaseICom):
    __tablename__ = 'Element'
    name_id = Column('element_id', Integer, nullable=False, unique=True)
    element_type = Column('element_type', String, ForeignKey('Element_type.name'), nullable=False) #foreign key to element type
    nodes = relationship('Node', secondary=NodeElement.__table__, backref='Element')
    properties = relationship('Property', Integer, ForeignKey('Property.property_id'), nullable=True)
    offset = Column(String)


class Property(BaseICom, BaseCOG):
    """
    TODO: COG to be concidered, what point has to be used?
    """
    name_id = Column('property_id', Integer, nullable=False, unique=True)
    cross_section = Column('cross-section')
