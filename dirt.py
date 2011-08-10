import os
import logging

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.view import view_config

from paste.httpserver import serve
import sqlite3

logging.basicConfig()
log = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))

# views
@view_config(route_name='index', renderer='index.mako')
def index_view(request):
    rs = request.db.execute("select id, number, description, uuid from record order by -id")
    records = [dict(id=row[0], number=row[1], description=row[2], uuid=row[3]) for row in rs.fetchall()]
    return {'records': records}

@view_config(route_name='record', renderer='record.mako')
def record_view(request):
    record_id = request.matchdict['record_id']
    rs = request.db.execute("select id, name, created, slave_id, checked_out, completed, success, results, task_type, platform from task where task.record_id = ?", (record_id,))
    tasks = [dict(id=row[0], name=row[1], created=row[2], slave_id=row[3], checked_out=row[4], completed=row[5], success=row[6], task_type=row[7], platform=row[8]) for row in rs.fetchall()]
    return {'tasks': tasks}

@view_config(route_name='task', renderer='task.mako')
def task_view(request):
    task_name = request.matchdict['task_name']
    rs = request.db.execute("select id, name, record_id, created, slave_id, checked_out, completed, success, results, task_type, platform from task where task.name = ?", (task_name,))
    tasks = [dict(id=row[0], name=row[1], record_id=row[2], created=row[3], slave_id=row[4], checked_out=row[5], completed=row[6], success=row[7], task_type=row[8], platform=row[9]) for row in rs.fetchall()]
    print tasks
    return {'tasks': tasks}

@view_config(route_name='record_new', renderer='record_new.mako')
def record_new_view(request):
    if request.method == 'POST':
        if request.POST.get('number') or request.POST.get('uuid'):
            # default values
            record_number = 0
            record_uuid = ''
            record_description = ''

            if request.POST.get('number'):
                record_number = request.POST.get('number')
            if request.POST.get('number'):
                record_uuid = request.POST.get('uuid')
            if request.POST.get('description'):
                record_description = request.POST.get('description')

            request.db.execute('insert into record (number, description, uuid) values (?, ?, ?)',
                               [record_number, record_description, record_uuid])
            request.db.commit()
            request.session.flash('New record was successfully added!')
            return HTTPFound(location=request.route_url('index'))
        else:
            request.session.flash('Please enter a number or UUID!')
    return {}

@view_config(route_name='task_new', renderer='task_new.mako')
def task_new_view(request):
    if request.method == 'POST':
        if request.POST.get('name'):
            type_name = request.POST.get('name')
            type_record_id = request.POST.get('record_id')
            type_created = request.POST.get('created')
            type_slave_id = request.POST.get('slave_id')
            type_checked_out = request.POST.get('checked_out')
            type_completed = request.POST.get('completed')
            type_success = request.POST.get('success')
            type_results = request.POST.get('results')
            type_task_type = request.POST.get('task_type')
            type_platform = request.POST.get('platform')


            request.db.execute('insert into task (name, record_id, created, slave_id, checked_out, completed, success, results, task_type, platform) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                [type_name,
                 type_record_id,
                 type_created,
                 type_slave_id,
                 type_checked_out,
                 type_completed,
                 type_success,
                 type_results,
                 type_task_type,
                 type_platform])

            request.db.commit()
            request.session.flash('New record was successfully added!')
            return HTTPFound(location=request.route_url('index'))
        else:
            request.session.flash('Please enter a number or UUID!')
    return {}

@view_config(context='pyramid.exceptions.NotFound', renderer='notfound.mako')
def notfound_view(self):
    return {}

# subscribers
@subscriber(NewRequest)
def new_request_subscriber(event):
    request = event.request
    settings = request.registry.settings
    request.db = sqlite3.connect(settings['db'])
    request.add_finished_callback(close_db_connection)

def close_db_connection(request):
    request.db.close()

@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    log.warn('Initializing database...')
    f = open(os.path.join(here, 'schema.sql'), 'r')
    stmt = f.read()
    settings = event.app.registry.settings
    db = sqlite3.connect(settings['db'])
    db.executescript(stmt)
    db.commit()
    f.close()

if __name__ == '__main__':
    # configuration settings
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['mako.directories'] = os.path.join(here, 'templates')
    settings['db'] = os.path.join(here, 'tasks.db')
    # session factory
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    # configuration setup
    config = Configurator(settings=settings, session_factory=session_factory)
    # routes setup
    config.add_route('index', '/')
    config.add_route('task_new', '/task_new')
    config.add_route('record_new', '/record_new')
    config.add_route('record', '/record/{record_id}')
    config.add_route('task', '/task/{task_name}')
    # static view setup
    config.add_static_view('static', os.path.join(here, 'static'))
    # scan for @view_config and @subscriber decorators
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    serve(app, host='127.0.0.1')

