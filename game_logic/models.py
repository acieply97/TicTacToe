from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship

from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///game_stats.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    session_id = Column(String(50))
    credits = Column(Integer, default=10)

    def __repr__(self):
        return f"Player(id={self.id}, username={self.username}, credits={self.credits}, session_id={self.session_id},)"


class GameStat(Base):
    __tablename__ = 'game_stats'
    id = Column(Integer, primary_key=True)
    player_1_id = Column(Integer, ForeignKey('player.id'))
    player_2_id = Column(Integer, ForeignKey('player.id'))
    result_player_1 = Column(String(10))
    result_player_2 = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow)

    player_1 = relationship('Player', foreign_keys=[player_1_id])
    player_2 = relationship('Player', foreign_keys=[player_2_id])

    def __repr__(self):
        return f"<GameStat(id={self.id}, player_1_id={self.player_1_id}, player_2_id={self.player_2_id}, " \
               f"result_p1={self.result_player_1}, result_p2={self.result_player_2}  timestamp={self.timestamp})>"


Base.metadata.create_all(engine)
