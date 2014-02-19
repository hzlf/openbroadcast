server installation
===================



vz node post-install
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    aptitude install build-essential python-setuptools supervisor git screen htop iftop bsd-mailx cron-apt locales ca-certificates


(configure email / postfix)

.. code-block:: bash

    nano /etc/aliases     # (map root to to sysadmin)
    nano /etc/postfix/transport   # (* smtp:[mx2.digris.ch])

    postalias /etc/aliases
    postmap /etc/postfix/transport

    /etc/init.d/postfix reload




vz nodes post-clone
~~~~~~~~~~~~~~~~~~~

on vz-host:

.. code-block:: bash

    nano /etc/vz/conf/<id>.conf # adapt ip and hostname



vz nodes
~~~~~~~~

node01
::::::

webhead

 - internal: 172.20.10.201
 - external: 95.211.179.43


.. code-block:: bash

    aptitude install nginx


node02
::::::

database-server

 - internal: 172.20.10.202

 - mariadb

.. code-block:: bash

    apt-get install python-software-properties
    apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
    add-apt-repository 'deb http://mirror.netcologne.de/mariadb/repo/10.0/debian wheezy main'

    apt-get update
    apt-get install mariadb-server


node03
::::::

messaging & cache server

 - internal: 172.20.10.203
 - external: 95.211.179.44


cache
*****************

aptitude install memcached


redis
*************************

.. code-block:: bash

    wget http://download.redis.io/releases/redis-2.8.5.tar.gz
    tar xzf redis-2.8.5.tar.gz
    cd redis-2.8.5
    make
    make install

    nano /etc/redis/redis.conf # see etc/
    nano /etc/supervisor/conf.d/redis.conf # see etc/

    supervisorctl reread
    supervisorctl update
    supervisorctl status


rabbit-mq
*************************

see: https://www.rabbitmq.com/install-debian.html

.. code-block:: bash

    rabbitmq-plugins enable rabbitmq_management

    rabbitmqctl add_user root <password>
    rabbitmqctl set_user_tags root administrator


http://172.20.10.203:15672/ # needs vpn connection






node04
::::::

development app-server

 - internal: 172.20.10.204
 - external: 95.211.179.45


node05
::::::

app-server

 - internal: 172.20.10.205
 - external: 95.211.179.46


node06
::::::

streaming-server

 - internal: 172.20.10.206
 - external: 95.211.179.47


node07
::::::

musicbrainz mirror

 - internal: 172.20.10.207


