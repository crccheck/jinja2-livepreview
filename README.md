Jinja2 Live Preview
===================

[![Build Status](https://travis-ci.org/crccheck/jinja-livepreview.svg)](https://travis-ci.org/crccheck/jinja2-livepreview)

If you've ever wondered how a Jinja2 filter would work in an Ansible template,
but cried at the thought of doing a run just to test a template, this is for
you.


Running the project
-------------------

### Via Docker

    docker run --rm -p 8080:8080 crccheck/jinja2-livepreview

If you want to change the port, specify the `PORT` environment variable like:

    docker run --rm -e PORT=5000 -p 5000:5000 crccheck/jinja2-livepreview


Developing
----------

    mkvirtualenv jinja2-livepreview --py=python3.5
    make install


Prior art
---------

* https://github.com/abourguignon/jinja2-live-parser Original by `abourguignon`
