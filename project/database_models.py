import hashlib
from dateutil import parser
from sqlalchemy import Column
from sqlalchemy import Integer, String, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy.sql import func

Base = declarative_base()


class UserLogins(Base):
    """
    Records for user logins.

    Primary keys are set in orm layer however this is to satisfy sqlalchemy requirement.
    TODO: Update primary key if database contains one, maybe timestamp
    """
    __tablename__ = "user_logins"

    # id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    user_id = Column(String(128), primary_key=True)
    device_type = Column(String(32), primary_key=True)
    masked_ip = Column(String(256), primary_key=True)
    masked_device_id = Column(String(256), primary_key=True)
    locale = Column(String(32), nullable=True, primary_key=True)
    app_version = Column(Integer, primary_key=True)
    create_date = Column(Date, default=func.now(), primary_key=True)

    @hybrid_property
    def ip(self):
        return self.masked_ip

    @ip.setter
    def ip(self, ip):
        self.masked_ip = ip

    @hybrid_property
    def device_id(self):
        return self.masked_device_id

    @device_id.setter
    def device_id(self, device_id):
        self.masked_device_id = device_id

    @validates('app_version')
    def _app_version(self, key, value):
        if type(value) == str:
            return int(value.split('.')[0])
        else:
            return value

    @validates('create_date')
    def _create_date(self, key, value):
        if type(value) == str:
            return parser.parse(value).date()
        else:
            return value

    @validates('masked_ip')
    def _mask_ip(self, key, value):
        """
        Conditionally mask in order to support transparent use of masked and unmasked values.
        Detection is based on the presence of a dash in the id.

        :param value: IPv4 or IPV6 address, either hashed or un-hashed
        :return: hashed address
        """
        if ':' in value or '.' in value:
            return hashlib.sha256(value.encode('utf-8')).hexdigest()
        else:
            return value

    @validates('masked_device_id')
    def _mask_device_id(self, key, value):
        """
        Conditionally mask in order to support transparent use of masked and unmasked values.
        Detection is based on the presence of a dash in the id.

        :param value: device id, either hashed or un-hashed
        :return: the hashed device id
        """
        if '-' in value:
            return hashlib.sha256(value.encode('utf-8')).hexdigest()
        else:
            return value
