from typing import Optional

from sqlalchemy import Column, BigInteger
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class Reputation(Base):
    __tablename__ = "reputations"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, index=True, nullable=False)
    scores: Mapped[int]
    link: Mapped[Optional[str]]
