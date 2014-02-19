#!/usr/bin/env python
from __future__ import with_statement
from fabric.api import local, settings, abort, run, cd, env
from fabric.contrib.console import confirm
import os

# glogal env
env.warn_only = True
env.supervisor = '/etc/supervisor/conf.d'
env.nginx = '/etc/nginx/sites-enabled'

env.skip_requirements = False
env.skip_db = False

def clean():
    local("find . -name '*.DS_Store' -type f -delete")
    local("find . -name '*.pyc' -type f -delete")

def tx_push():
    local('cd website && ./manage.py makemessages --all --ignore=socialregistration/* --ignore=filer/*')
    local('tx push -t -s') 

def tx_pull():
    local('tx pull')
    local('cd website && ./manage.py compilemessages') 
    

"""
Definition instances
"""
def openbroadcast_ch():
    env.site_id = 'openbroadcast.ch'
    env.hosts = ['node05.scd.hazelfire.com']
    #env.hosts = ['node05.daj.anorg.net']
    #env.git_url = 'git://github.com/hzlf/openbroadcast.git'
    env.git_url = 'git@lab.hazelfire.com:hazelfire/obp/openbroadcast-ch.git'
    #env.git_branch = 'development'
    env.git_branch = 'cleanup'
    env.path = '/var/www/openbroadcast.ch'
    env.storage = '/storage/www_data/openbroadcast.ch'
    env.user = 'root'

def stage_openbroadcast_ch():
    env.site_id = 'openbroadcast.ch'
    env.hosts = ['172.20.10.204']
    #env.hosts = ['node05.daj.anorg.net']
    #env.git_url = 'git://github.com/hzlf/openbroadcast.git'
    env.git_url = 'git@lab.hazelfire.com:hazelfire/obp/openbroadcast-ch.git'
    #env.git_branch = 'development'
    env.git_branch = 'cleanup'
    env.path = '/var/www/openbroadcast.ch'
    env.storage = '/nas/storage/stage.openbroadcast.ch'
    env.user = 'root'

def prod_openbroadcast_ch():
    env.site_id = 'openbroadcast.ch'
    env.hosts = ['172.20.10.205']
    #env.hosts = ['node05.daj.anorg.net']
    #env.git_url = 'git://github.com/hzlf/openbroadcast.git'
    env.git_url = 'git@lab.hazelfire.com:hazelfire/obp/openbroadcast-ch.git'
    #env.git_branch = 'development'
    env.git_branch = 'cleanup'
    env.path = '/var/www/openbroadcast.ch'
    env.storage = '/nas/storage/prod.openbroadcast.ch'
    env.user = 'root'

    
    
def build_ci():
    local('wget %s' % ('http://ci.lab.anorg.net/job/ch-openbroadcast/build?token=BUILD'))
    

def skip_req():
    env.skip_requirements = True

def skip_db():
    env.skip_db = True

def deploy():
    try:
        # stop app-server
        run('supervisorctl stop %s' % env.site_id)

    except Exception, e:
        pass
    """
    """
    with cd(env.path):  
        
        """
        create project directory
        """
        try:
            run('mkdir -p %s' % env.path)
        except Exception, e:
            pass
        
        """
        create directory to save the local_config
        """
        try:
            run('mkdir config')
        except Exception, e:
            pass
        
        try:
            run('cp src/website/local_settings.py config/')  
        except Exception, e:
            pass
        
        """
        recreate src directory
        """    
        try:
            run('rm -Rf src')
        except Exception, e:
            pass
        
        run('mkdir src')

        
    with cd(env.path + '/src'):
        
        """
        aquire code from repository
        """
        run('git init')
        run('git remote add -t %s -f origin %s' % (env.git_branch, env.git_url))
        run('git checkout %s' % (env.git_branch))
        
    with cd(env.path): 

        """
        copy back the local_settings
        """
        try:
            run('cp config/local_settings.py src/website/')
        except Exception, e:
            pass
            
        
        """
        virtualenv and requirements
        """
        try:
            run('virtualenv /srv/%s' % env.site_id)
        except Exception, e:
            pass

        """
        hacks
        """
        try:
            # pip - version < 1.5 needed to allow external modules
            run('/srv/%s/bin/pip install pip==1.4.1' % (env.site_id))
        except Exception, e:
            pass

        try:
            # pre-install numpy, does not work through requirements
            run('/srv/%s/bin/pip install numpy' % (env.site_id))
        except Exception, e:
            pass

            
        """
        install project requirements
        """
        if not env.skip_requirements:
            #run('pip -E /srv/%s install -r %s' % (env.site_id, 'src/website/requirements/requirements.txt'))
            run('/srv/%s/bin/pip install -r  %s --allow-all-external' % (env.site_id, 'src/website/requirements/requirements.txt'))
        
            
        """
        linking storage directories
        """
        try:
            run('ln -s %s/media %s/src/website/media' % (env.storage, env.path))
            run('ln -s %s/smedia %s/src/website/smedia' % (env.storage, env.path))
            run('ln -s %s/static %s/src/website/static' % (env.storage, env.path))
        except Exception, e:
            pass
            
            
        """
        linking config files
        """
        try:
            run('rm %s/%s.conf' % (env.supervisor, env.site_id))
            run('ln -s %s/src/conf/%s.supervised.conf %s/%s.conf' % (env.path, env.site_id, env.supervisor, env.site_id))
        except Exception, e:
            pass
            
        """
        additional supervisor configs
        """
            
        try:
            run('rm %s/%s' % (env.nginx, env.site_id))
            run('ln -s %s/src/conf/%s.nginx.conf %s/%s' % (env.path, env.site_id, env.nginx, env.site_id))
        except Exception, e:
            pass
            
        """
        run migrations
        """
        if not env.skip_db:
            try:
                run('/srv/%s/bin/python /%s/src/website/manage.py syncdb' % (env.site_id, env.path))
                run('/srv/%s/bin/python /%s/src/website/manage.py migrate' % (env.site_id, env.path))
            except Exception, e:
                pass
            
        """
        staticfiles & compress
        """
        
        
        
        try:
            with cd(env.path + '/src/website/site-static/'):
                pass
                #run('rm -R css/*')
                #run('/var/lib/gems/1.8/gems/compass-0.11.7/bin/compass compile -c config-production.rb')
        except Exception, e:
            pass        
        
        try:
            run('/srv/%s/bin/python /%s/src/website/manage.py collectstatic --noinput --verbosity=0' % (env.site_id, env.path))
            run('/srv/%s/bin/python /%s/src/website/manage.py compress -f' % (env.site_id, env.path))
        except Exception, e:
            pass


        """
        generate git changelog
        git log > changelog.txt
        """
        try:
            with cd(env.path + '/src/website/'):
                run('git log > changelog.txt')
        except Exception, e:
            pass



            
        """
        (re)start supervisor workers
        """
        try:
            # restart gunicorn webserver
            run('supervisorctl restart %s' % env.site_id)
            # restart gunicorn celeryd-worker
            #run('supervisorctl restart worker.celery.%s' % env.site_id)
            #run('supervisorctl restart worker.import.%s' % env.site_id)
            #run('supervisorctl restart worker.convert.%s' % env.site_id)
            # restart other supervisor services
            #run('supervisorctl restart echoprint.%s' % env.site_id)
            #run('supervisorctl restart ttserver.%s' % env.site_id)
            #run('supervisorctl restart pushy.%s' % env.site_id)
            # present current status
            run('supervisorctl status | grep %s' % env.site_id)
        except Exception, e:
            pass
        
        


def restart():
            
    """
    (re)start supervisor workers
    """
    try:
        # restart gunicorn webserver
        run('supervisorctl restart %s' % env.site_id)
        # restart gunicorn celeryd-worker
        run('supervisorctl restart worker.celery.%s' % env.site_id)
        run('supervisorctl restart worker.import.%s' % env.site_id)
        run('supervisorctl restart worker.convert.%s' % env.site_id)
        run('supervisorctl restart worker.complete.%s' % env.site_id)
        run('supervisorctl restart worker.process.%s' % env.site_id)
        # restart other supervisor services
        run('supervisorctl restart echoprint.%s' % env.site_id)
        run('supervisorctl restart ttserver.%s' % env.site_id)
        run('supervisorctl restart pushy.%s' % env.site_id)
        
        run('supervisorctl status')
        
    except Exception, e:
        pass

def stop_workers():

    """
    (re)start supervisor workers
    """
    try:
        # restart gunicorn celeryd-worker
        run('supervisorctl stop worker.celery.%s' % env.site_id)
        run('supervisorctl stop worker.import.%s' % env.site_id)
        run('supervisorctl stop worker.convert.%s' % env.site_id)
        run('supervisorctl stop worker.complete.%s' % env.site_id)
        run('supervisorctl stop worker.process.%s' % env.site_id)
        # restart other supervisor services
        run('supervisorctl stop echoprint.%s' % env.site_id)
        run('supervisorctl stop ttserver.%s' % env.site_id)
        run('supervisorctl stop pushy.%s' % env.site_id)

        run('supervisorctl status')

    except Exception, e:
        pass


def doc_make():
    local('cd doc && make html')

def doc_push():
    local('rsync -a doc/_build/html root@node05.daj.anorg.net:/var/www/doc.openbroadcast.ch')
