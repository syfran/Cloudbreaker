Cloudbreaker is an application to crack passwords in the cloud. It is built on
the pyramid framework, boto library and requests library.

It requires python 2.7 in order to work with the boto python library.

The AMIs are currently not publicly available, so you will need to create the
appropriate AMI the JTR, oclHashcat and an appropriate wordlist installed. You
can then set the various variables in amazon.py and the password source's size
in hashtracker.py.

To run it you must also set up three environment variables:

1. AWS_ACCESS_KEY_ID - This is you amazon access key id for boto.
2. AWS_SECRET_ACCESS_KEY - This is the access key secret for boto.
3. CLOUDBREAKER_HTTP_PASS - This is the HTTP basic auth password, the username
    is cloudbreaker.

It currently has only been tested in development mode with pserve, but should
be capable of running under any wsgi server if you follow pyramid's setup
instructions.
