from sqlite_helper import Base
from sqlalchemy import Column, String, Integer,Float

class Donor(Base):
    __tablename__ = 'donation_info'

    id = Column(Integer,autoincrement=True,primary_key=True)
    name =Column(String(80),nullable=False)
    amount =Column(Float,nullable=False)
    remark =Column(String(80),nullable=True)
    operator =Column(String(240), unique=False)

    def __init__(self, name=None, amount=None,remark=None,operator=None):
        self.name = name
        self.amount=amount
        self.remark=remark
        self.operator=operator

