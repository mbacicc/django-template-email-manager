---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: page
title: Home
permalink: /
nav_order: 0
---


<!-- PROJECT LOGO -->
<br />
<p align="center">
    <img src="img/django-template-email-manager.png" alt="Django Template Email Manager" width="160" >
</p>
  <h1 align="center">Django Template Email Manager</h1>

  <p align="center">
    A free and open source app to manage email queues from any django project
    <br />
    <a href="https://mbacicc.github.io/django-template-email-manager/"><strong>Explore the documentation</strong></a>
    <br />
  </p>
<hr>

## Info

Template Email Manager is a Django App that manages all the email communications of your Django project. You can create multiple sending accounts, HTML templates with attached images and email receivers. Everything is run-time customizable, since all the parameters are stored in DB. All messages are stored in a DB based queue.

## Features

- Allows you to use multiple source e-mail provider and address on the same Django project
- Each configured email provider has its own attributes (max send attempts, delay between retries, and so on...)
- You can add and edit TXT and HTML e-mail templates at run-time, without the need to change the code
- You can attach picture and/or other format attachment to the e-mails
- Automatic queue management using [Django Background Tasks](https://github.com/arteria/django-background-tasks)
- Storage of all added and processed e-mails with status and logs