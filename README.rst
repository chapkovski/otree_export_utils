========================================================================
Exporting data for the specific sessions
========================================================================

Author: Philipp Chapkovski (chapkovski@gmail.com)

Installation:
***************
1. **Either**:

- type ``pip install otree-custom-export`` in your terminal window.


2. **or**:

-  clone exisiting project ``git clone https://github.com/chapkovski/otree_export_utils`` and copy the
``otree_export_utils`` folder into your project folder, next to the apps of your module.

3. After that add "otree_export_utils" to your INSTALLED_APPS section of ``settings.py`` file like this::

    INSTALLED_APPS = [
        'otree',
        'otree_export_utils',
    ]
