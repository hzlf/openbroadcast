App Server(s)
===================


Main Application Server
-----------------------

 - node04: stage.openbroadcast.ch
 - node05: prod.openbroadcast.ch

both share the same setup



Chromaprint / AcoustID
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    aptitude install install libchromaprint-tools libchromaprint-dev


Echoprint installation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    aptitude install install ffmpeg libboost1.42-dev libtag1-dev zlib1g-dev

    cd
    cd src
    git clone https://github.com/echonest/echoprint-codegen.git
    cd echoprint-codegen
    make make install

    echoprint-codegen # test...




Echoprint server installation
~~~~~~~~~~~~~~~~~~~~~~

Only used on stage server. Echoprint server for production is located on node03.

.. code-block:: bash

    aptitude install default-jre tokyotyrant

    cd
    cd src
    git clone https://github.com/echonest/echoprint-server.git
    cd echoprint-server


    mkdir -p /srv/openbroadcast.ch/service
    cp -Rp solr/solr /srv/openbroadcast.ch/service/
    cd /srv/openbroadcast.ch/service/solr

    # solr
    java -Dsolr.solr.home=/srv/openbroadcast.ch/service/solr/solr/ -Djava.awt.headless=true -jar start.jar

    # tokyo-tyrant
    /usr/sbin/ttserver -port 1978 -thnum 4 -kl -pid /var/ttserver/pid -log /var/log/ttserver.log /var/ttserver/casket.tch#bnum=1000000




