Overview
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

See :doc:`messaging`

:guilabel:`&Cancel`

:kbd:`Control-x Control-f`

:mailheader:`Content-Type`

:menuselection:`Start --> Programs`





node04
::::::

development app-server

 - internal: 172.20.10.204
 - external: 95.211.179.45

See :doc:`appserver`


node05
::::::

app-server

 - internal: 172.20.10.205
 - external: 95.211.179.46

See :doc:`appserver`


node06
::::::

streaming-server

 - internal: 172.20.10.206
 - external: 95.211.179.47


node07
::::::

musicbrainz mirror

 - internal: 172.20.10.207


