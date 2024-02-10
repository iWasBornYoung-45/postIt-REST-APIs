from database import Base
from sqlalchemy import Column, String, Boolean, UUID, Integer, BigInteger, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

class Posts(Base):
    __tablename__ = "Posts"
    id = Column(UUID, primary_key=True, nullable=False, server_default=text('gen_random_uuid()'))
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    content_type = Column(String, nullable=False, server_default='tech')
    published = Column(Boolean, server_default='TRUE', nullable=False)
    added_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    op_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    op = relationship('Users')

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(BigInteger, nullable=False, unique=True)
    password = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Upvotes(Base):
    __tablename__ = "upvotes"
    post_id = Column(UUID, ForeignKey('Posts.id', ondelete="CASCADE"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), primary_key=True, nullable=False)



