---
layout: page
title: Installation
permalink: /installation/
nav_order: 1
---


- Install it from PyPI inside your virtualenv: 
  
```shell
pip install django-template-email-manager
```

- Add `template_email_manager` to the list of installed app in your project (INSTALLED_APPS) in `setup.py`:

```python
INSTALLED_APPS = [
    ...
    'template_email_manager',
    ...
]
```

- Run `python manage.py migrate` from your virtualenv to create the database structure.
- Create your template and save it on your DB and start using it or use the demo fixture
- Where you want to send templated email add this import:

```python
from template_email_manager.commands import add_email_to_queue
```

and add this code to add a mail to the send queue:

```python
# context dict for the template variables replacement
context = {
    'var1': value1,
    'var2': value2
}
add_email_to_queue('template_name', context)
```

`template_name` must much the name of a template stored in the model `HTMLTemplate`
