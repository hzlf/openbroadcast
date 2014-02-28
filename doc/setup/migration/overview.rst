Platform - Legacy-data Migration
################################


Preparation
*********************



Configure the needed database connections:
==========================================

local_settings.py

.. code-block:: bash

    DATABASES = {

        'default': {
            ***
        },
        'legacy': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'legacy_openbroadcast_medialibrary',
            'USER': 'openbroadcast',
            'PASSWORD': '********************',
            'HOST': '172.20.10.202',
        },
        'legacy_legacy': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'legacy_openbroadcast',
            'USER': 'openbroadcast',
            'PASSWORD': '********************',
            'HOST': '172.20.10.202',
        },
    }



Database
========

.. note::

    Tables on ":abbr:`legacy-legacy (a.k.a. ELGG)`" have to be altered!


.. code-block:: sql

    ALTER TABLE `elgg_cm_master` ADD `migrated` DATETIME  NULL  AFTER `locked_userident`;

.. note::

    Flags on ":abbr:`legacy (a.k.a. openbroadcast 1.5)`" have to be altered!


.. code-block:: sql

    ALTER TABLE `elgg_cm_master` ADD `migrated` DATETIME  NULL  AFTER `locked_userident`;


File storage/access
===================

Files from the legacy-installation must be mounted on the application-server. Configuration:

.. code-block:: bash

    LEGACY_STORAGE_ROOT = '/nas/prod/ml/'


.. note::

    `LEGACY_STORAGE_ROOT` is the directory that contains the main `media` folder!!




Migration tools
*********************

Migration tools live in the `obp_legacy` app.

.. code-block:: bash

    ./manage.py migrate_legacy --help

The relevant options here are:

.. code-block:: bash

      --type=OBJECT_TYPE    Entity type (media, release, label, artist, user, group, playlist)
      --id=ID               Specify an ID to run migration on
      --legacy_id=LEGACY_ID Specify a Legacy-ID to run migration on
      --limit=LIMIT         How many rows to process... defaults to 100


Single objects (only media a.k.a. "Track") can be migrated like:

http://openbroadcast.ch/en/content/library/media/1-barbarella/detail.html

.. code-block:: bash

    ./manage.py migrate_legacy --type=media --legacy_id=1