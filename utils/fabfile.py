from fabric.api import cd, run, sudo, put
from cStringIO import StringIO


base_dir = '/usr/local'
hostname = 'searx.me'
searx_dir = base_dir + '/searx'
searx_ve_dir = searx_dir + '/searx-ve'
current_user = run('whoami').stdout.strip()

uwsgi_file = '''
[uwsgi]
# Who will run the code
uid = {user}
gid = {user}

# Number of workers
workers = 8

# The right granted on the created socket
chmod-socket = 666

# Plugin to use and interpretor config
single-interpreter = true
master = true
plugin = python

# Module to import
module = searx.webapp

# Virtualenv and python path
virtualenv = {searx_ve_dir}
pythonpath = {searx_dir}
chdir = {searx_dir}/searx
'''.format(user=current_user,
           searx_dir=searx_dir,
           searx_ve_dir=searx_ve_dir)

nginx_config = '''
server {{
    listen 80;
    server_name {hostname};
    server_name www.{hostname};
    root /usr/local/searx;

    location / {{
        include uwsgi_params;
        uwsgi_pass unix:/run/uwsgi/app/searx/socket;
    }}
}}
'''.format(hostname=hostname)


def stop():
    sudo('/etc/init.d/uwsgi stop')


def start():
    sudo('/etc/init.d/uwsgi start')


def restart():
    sudo('/etc/init.d/uwsgi restart')


def init():
    if not run('test -d ' + searx_dir, warn_only=True).failed:
        return

    sudo('apt-get update')

    sudo('apt-get install git'
         ' build-essential'
         ' libxslt-dev'
         ' python-dev'
         ' python-virtualenv'
         ' python-pybabel'
         ' zlib1g-dev'
         ' uwsgi'
         ' uwsgi-plugin-python'
         ' nginx')

    sudo('mkdir -p ' + base_dir)

    put(StringIO(nginx_config), '/etc/nginx/sites-enabled/searx', use_sudo=True)
    sudo('/etc/init.d/nginx restart')

    with cd(base_dir):
        sudo('git clone https://github.com/asciimoo/searx')

    sudo('chown -R {user}:{user} {searx_dir}'.format(user=current_user, searx_dir=searx_dir))
    put(StringIO(uwsgi_file), searx_dir + '/uwsgi.ini')
    sudo('ln -s {0}/uwsgi.ini /etc/uwsgi/apps-enabled/searx.ini'.format(searx_dir))

    run('virtualenv {0}'.format(searx_ve_dir))

    with cd(searx_dir):
        run('source {0}/bin/activate && pip install -r requirements.txt'.format(searx_ve_dir))

    start()


def deploy():
    init()

    with cd(searx_dir):
        run("git stash", warn_only=True)
        run("git pull origin master")
        run("git stash pop", warn_only=True)

    restart()


def clean():
    sudo('rm -rf {searx_dir}'.format(searx_dir=searx_dir), warn_only=True)
    sudo('rm /etc/uwsgi/apps-enabled/searx.ini', warn_only=True)
    sudo('rm /etc/nginx/sites-enabled/searx', warn_only=True)
