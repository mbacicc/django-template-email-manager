![PyPI](https://img.shields.io/pypi/v/django-template-email-manager)
![GitHub](https://img.shields.io/github/license/mbacicc/django-template-email-manager)
[![Created Badge](https://badges.pufler.dev/created/mbacicc/django-template-email-manager)](https://github.com/mbacicc/django-template-email-manager)
[![Downloads](https://pepy.tech/badge/django-template-email-manager)](https://pepy.tech/project/django-template-email-manager)
[![Downloads](https://static.pepy.tech/personalized-badge/django-template-email-manager?period=month&units=international_system&left_color=black&right_color=orange&left_text=downloads/month)](https://pepy.tech/project/django-template-email-manager)
[![Visits Badge](https://badges.pufler.dev/visits/mbacicc/django-template-email-manager)](https://github.com/mbacicc/django-template-email-manager/)
![Commits Badge](https://badges.pufler.dev/commits/monthly/mbacicc)


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/mbacicc/django-template-email-manager/">
    <img src="docs/img/django-template-email-manager.png" alt="Django Template Email Manager" width="160" >
  </a>
</p>
  <h1 align="center">Django Template Email Manager</h1>

  <p align="center">
    A free and open source app to manage email queues from any django project
    <br />
    <a href="https://mbacicc.github.io/django-template-email-manager/"><strong>Explore the documentation</strong></a>
    <br />
    <br />
  </p>

## Table of Content
- [Table of Content](#table-of-content)
- [Info](#info)
- [Features](#features)
- [Installation and Use](#installation-and-use)

## Info

Template Email Manager is a Django App that manages all the email communications of your Django project. You can create multiple sending accounts, HTML templates with attached images and email receivers. Everything is run-time customizable, since all the parameters are stored in DB. All messages are stored in a DB based queue.

## Features

- Allows you to use multiple source e-mail provider and address on the same Django project
- Each configured email provider has its own attributes (max send attempts, delay between retries, and so on...)
- You can add and edit TXT and HTML e-mail templates at run-time, without the need to change the code
- You can attach picture and/or other format attachment to the e-mails
- Automatic queue management using [Django Background Tasks](https://github.com/arteria/django-background-tasks)
- Storage of all added and processed e-mails with status and logs

## Installation and Use

- Install it from PyPI inside your virtualenv: 

        pip install django-template-email-manager

- Add `template_email_manager` to the list of installed app in your project (INSTALLED_APPS):

        INSTALLED_APPS = [
            ...
            'template_email_manager',
            ...
        ]

- Run `python manage.py migrate` from your virtualenv to create the database structure.

- Create your template and save it on your DB and start using it or use the demo fixture
  
- Where you want to send templated email add this import:

        from template_email_manager.commands import add_email_to_queue

    and add this code to add a mail to the send queue:

            # context dict for the template variables replacement
            context = {
                'var1': value1,
                'var2': value2
            }
            add_email_to_queue('template_name', context)

    `template_name` must much the name of a template stored in the model `HTMLTemplate`

Please refer to the [Docs](https://mbacicc.github.io/django-template-email-manager/) for detailed info on how to install and use it.

<!-- ## System Architecture -->

<!-- ## Screenshots -->

<!-- ## FAQ -->
