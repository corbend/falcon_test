import uuid
from wsgiref import simple_server

import falcon
import json

from sqlalchemy import schema, types
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import select
from jinja2 import Template

metadata = schema.MetaData()

notify_table = schema.Table(
    'notify', metadata,
    schema.Column('id', types.Integer, primary_key=True),
    schema.Column('datetime', types.DateTime, default=falcon.datetime.datetime.now),
    schema.Column('transaction_id', types.Unicode(255), default=u''),
)

engine = create_engine('sqlite:///:memory:', echo=True)
metadata.bind = engine

metadata.create_all(checkfirst=True)


class NotifyResource(object):

    def on_get(self, req, resp):

        connection = engine.connect()

        s = notify_table.select().order_by(notify_table.c.datetime.desc()).limit(1)
        result = connection.execute(s)

        rows = []
        for row in result:
            rows.append(row)

        template = Template('{%for notify in notifies%}{{notify.datetime}} - {{notify.transaction_id}}{%endfor%}')
        template_text = template.render(notifies=rows)

        ins = notify_table.insert(
            values=dict(transaction_id=str(uuid.uuid4()))
        )
        connection.execute(ins)
        connection.close()

        resp.body = template_text

app = falcon.API()
app.add_route('/notify', NotifyResource())

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()