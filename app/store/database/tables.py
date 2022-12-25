# from .models import Base
# from sqlalchemy import (
#     Column,
#     String,
#     Integer,
#     Float,
#     DateTime,
#     ForeignKey,
#     func
# )
#
#
# # Создаем модель таблицы Свойства
# class Frames(Base):
#     __tablename__ = 'frame'
#     id = Column(Float, primary_key=True)
#     comment = Column(String, default=None)
#
#
# class Stringers(Base):
#     __tablename__ = 'stringer'
#     id = Column(Float, primary_key=True)
#     comment = Column(String, default=None)
#
#
# class SectionProperty(Base):
#     __tablename__ = 'section property'
#
#     id = Column(String, primary_key=True)
#     area = Column(Float, nullable=False)
#     inertia_xx = Column(Float, nullable=False)
#     inertia_yy = Column(Float, nullable=False)
#     inertia_zz = Column(Float, nullable=False)
#     cog_x = Column(Float, nullable=False)
#     cog_y = Column(Float, nullable=False)
#     cog_z = Column(Float, nullable=False)
#     comment = Column(String, default=None)
#
#
# class Message(Base):
#     __tablename__ = "message"
#     id = Column(Integer, primary_key=True)
#     text = Column(String, nullable=False)
#     created = Column(DateTime, nullable=False)