import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

class VirusModel(Model):
    class Meta:
        table_name = os.environ.get("APP_TABLE_NAME", "")
        region = 'eu-west-1'

    modelName = UnicodeAttribute(default='Virus', attr_name="PK", hash_key=True)
    uuid = UnicodeAttribute(range_key=True, attr_name="SK")
