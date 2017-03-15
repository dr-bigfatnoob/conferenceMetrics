"""Copyright 2012-2013
Eindhoven University of Technology (Bogdan Vasilescu and Alexander Serebrenik) and
University of Mons (Tom Mens)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>."""

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import relationship, backref
#from sqlalchemy.ext.associationproxy import association_proxy
import sqlalchemy;
import string

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
metadata = Base.metadata


person_paper = Table('authorship', metadata,
                     Column('person_id', Integer, ForeignKey('persons.id')),
                     Column('paper_id', Integer, ForeignKey('papers.id')))


class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    gender = Column(String(10))
    
    def __init__(self, name, gender=None):
        self.name = name.lower()
        self.gender = gender

    def __repr__(self):
        return "<Person('%s')>" % (self.name)


class Venue(Base):
    __tablename__ = 'venues'
    id = Column(Integer, primary_key=True)
    acronym = Column(String(20), nullable=False)
    name = Column(String(200))
    impact = Column(Integer)
    is_conference = Column(Boolean)

    def __init__(self, acronym, impact, name=None, is_conference=True):
        self.acronym = acronym
        self.impact = impact
        self.name = name
        self.is_conference = is_conference

    def __repr__(self):
        if self.is_conference:
            return "<Conference('%s')>" % self.acronym
        else:
            return "<Journal('%s')>" % self.acronym


class SubmissionsCount(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey('venues.id'))
    year = Column(Integer)
    number = Column(Integer)

    venue = relationship(Venue, backref="submissions")

    def __init__(self, year, number):
        self.year = year
        self.number = number


class PCMembership(Base):
    __tablename__ = 'pc_membership'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'))
    venue_id = Column(Integer, ForeignKey('venues.id'))
    year = Column(Integer)
    role = Column(String(100))
    
    def __init__(self, year, role):
        self.year = year
        self.role = role
    
    venue = relationship(Venue, backref="pc_membership")
    pcmember = relationship(Person, backref="pc_membership")    

class Paper(Base):
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey('venues.id'))
    year = Column(Integer)
    title = Column(String(500))
    pages = Column(String(30))
    num_pages = Column(Integer)
    session_h2 = Column(String(100))
    session_h3 = Column(String(100))
    main_track = Column(Boolean)
    ref_id = Column(String(100))
    cites = Column(String(10000))
    abstract = Column(String(50000))
    
    '''Many to many Author<->Paper'''
    authors = relationship('Person', secondary=person_paper, backref='papers')

    '''One to many Conference<->Paper'''
    venue = relationship("Venue", backref=backref('papers', order_by=id))

    def __init__(self, venue, year, title, pages, num_pages, session_h2, session_h3, selected=False):
        self.venue = venue
        self.year = year
        self.title = Paper.de_punctuate(title)
        self.pages = pages
        self.num_pages = num_pages
        self.session_h2 = session_h2.strip()
        self.session_h3 = session_h3.strip()
        self.main_track = selected
        self.ref_id = None
        self.cites = None
        self.abstract = None

    def __repr__(self):
        return "<Paper('%s, %d, %s')>" % (self.venue, self.year, self.title)

    @staticmethod
    def de_punctuate(s):
        return reduce(lambda s1, c: s1.replace(c, ''), string.punctuation, s).strip()


def initDB(engine):
    metadata.create_all(engine) 
    print 'Database structure created'


def _main():
    engine = sqlalchemy.create_engine("mysql://root:root@localhost/conference_metrics")
    initDB(engine)
