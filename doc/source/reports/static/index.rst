.. _static_agents:

Static agents
*************

In this scenario Shaker runs tests on pre-deployed static agents. The scenario
can be used for Shaker integration testing.

**Scenario**:

.. code-block:: yaml

    deployment:
      agents:
      - id: the-agent
        mode: alone
    description: In this scenario Shaker runs tests on pre-deployed static agents. The
      scenario can be used for Shaker integration testing.
    execution:
      tests:
      - class: shell
        program: ls -al
        sla:
        - '[type == ''agent''] >> (stderr == '''')'
        title: List all files
      - class: shell
        script: '#!/bin/bash
          echo "hello world"
          '
        sla:
        - '[type == ''agent''] >> (stdout & ''.*hello world.*'')'
        title: Run sample script
    file_name: /Users/ilyashakhat/Developer/shaker/shaker/scenarios/misc/static_agent.yaml
    title: Static agents

**Errors**:

.. code-block:: yaml

    agent: the-agent
    command:
      data: '#!/bin/bash
        echo "hello world"
        '
      type: script
    concurrency: 1
    executor: shell
    id: 2b521592-785c-4513-80c8-1643ceb6d9db
    node: null
    scenario: Static agents
    schedule: 1470413721.620275
    status: lost
    test: Run sample script
    type: agent

