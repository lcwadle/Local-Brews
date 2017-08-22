import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Float

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class Brewery(Base):
    __tablename__ = 'brewery'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    created_date = Column(Integer)
    website = Column(String(250))
    city = Column(String(25))
    state = Column(String(25))
    image_link = Column(String(25))
    description = Column(String(250))

class Beer(Base):
    __tablename__ = 'beer'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    style = Column(String(250))
    abv = Column(String(5))
    ibu = Column(Integer)
    srm = Column(Integer)
    og = Column(Integer)
    ingredients = Column(String(250))
    description = Column(String(250))
    brewery_id = Column(Integer, ForeignKey('brewery.id'))
    brewery = relationship(Brewery)
    image_link = Column(String(25))

    @property
    def serialize(self):
        return {
        'name' : self.name,
        'description' : self.description,
        'id' : self.id,
        'style' : self.style,
        'abv' : self.abv,
        'ibu' : self.ibu,
        'srm' : self.srm,
        'og' : self.og,
        'ingredients' : self.ingredients,
        'image_link' : self.image_link,
        }

engine = create_engine('sqlite:///localbreweries.db')

Base.metadata.create_all(engine)
