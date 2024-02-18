from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Session, declarative_base, relationship


Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chat'
    chat = Column(Integer, primary_key=True)
    config = relationship("Config", uselist=False, back_populates="chat")

    def __repr__(self) -> str:
        return f'Chat id: {self.chat}'


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chat.chat'))
    area = Column(JSON)
    rooms_count = Column(JSON)
    send_parsing_file = Column(JSON)
    location = Column(String(200))
    already_exists = Column(DateTime)
    mail = Column(String(200))
    chat = relationship('Chat', back_populates='config')

    def __repr__(self):
        return f'Конфиг для chat_id : {self.chat_id}'

    def bulk_update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)


def start_session() -> Session:
    engine = create_engine('sqlite:///sqlite.db', echo=False)
    session = Session(engine)
    Base.metadata.create_all(engine)
    return session
