Reset plattform to restart migration from `zero`
################################################


Remove all files on storage server
**********************************

.. note::

    Make sure to be in the right directory!!!!!!!!!!!!!!!!
    for stage this is:

    `/nas/storage/stage.openbroadcast.ch/`


.. code-block:: bash

    rm -R static/*
    rm -R smedia/*
    rm -R doc/*
    rm -R media/*



Reset legacy databases
**********************


Tables on ":abbr:`legacy-legacy (a.k.a. ELGG)`"

.. code-block:: sql

    UPDATE `elgg_cm_master` SET `migrated` = NULL WHERE `ident` > '0';


Tables on ":abbr:`legacy (a.k.a. Music Library)`"

.. code-block:: sql

    UPDATE `medias` SET `migrated` = NULL WHERE `id` > '0';
    UPDATE `artists` SET `migrated` = NULL WHERE `id` > '0';
    UPDATE `labels` SET `migrated` = NULL WHERE `id` > '0';
    UPDATE `releases` SET `migrated` = NULL WHERE `id` > '0';


