# BrainRefresh

> Our platform offers a unique and interactive way to prepare for technical interviews and refresh forgotten knowledge in web development and Python. With a collection of challenging quizzes and tests, users can assess their skills and identify areas for improvement. Our platform also provides in-depth explanations and resources to help users deepen their understanding and become interview-ready. Whether you're a seasoned developer or just starting out, our platform is the perfect tool to take your skills to the next level.


## Tests

---

### Type checks

Running type checks with mypy:

    $ mypy brainrefresh

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

### Celery

This app comes with Celery.

To run a celery worker:

``` bash
cd brainrefresh
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.

### Email Server

[MailHog](https://github.com/mailhog/MailHog) running, to view messages that are sent by your application, open your browser and go to `http://127.0.0.1:8025`

## Deployment

---

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).
