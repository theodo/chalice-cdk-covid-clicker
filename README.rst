REST API backed by Amazon DynamoDB
==================================

This template provides a REST API that's backed by an Amazon DynamoDB table.
This application is deployed using the AWS CDK.

For more information, see the `Deploying with the AWS CDK
<https://aws.github.io/chalice/tutorials/cdk.html>`__ tutorial.


Quickstart
----------

Requirements
############

CDK
***

First, you'll need to install the AWS CDK if you haven't already.
The CDK requires Node.js and npm to run.
See the `Getting started with the AWS CDK
<https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html>`__ for
more details.

::

  $ npm install -g aws-cdk

AWS Cli
*******

`Install guide <https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html>`__

You must also have an `AWS profile configured <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html>`__.

Python 3.9
**********

Use `pyenv <https://github.com/pyenv/pyenv>`__ to easily manage your python versions

Pipenv
******

`Install guide <https://github.com/pypa/pipenv>`__

Install
#######

1. Install the dependencies and create the virtual env

::

  $ pipenv install

2. Activate the virtual env

::

  $ pipenv shell


3. If it's the first time you use the CDK on this account you'll need to bootstrap it.

::

  $ cd infrastructure
  $ cdk bootstrap --profile <your aws profile>

4. Deploy the backend

::

  $ cd infrastructure
  $ cdk deploy --profile <your aws profile>


Project layout
--------------

This project template combines a CDK application and a Chalice application.
These correspond to the ``infrastructure`` and ``runtime`` directory
respectively.  To run any CDK CLI commands, ensure you're in the
``infrastructure`` directory, and to run any Chalice CLI commands ensure
you're in the ``runtime`` directory.
