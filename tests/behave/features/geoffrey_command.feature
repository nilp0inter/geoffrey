Feature: Geoffrey must have a neat user interface 

  Scenario: The first thing a user do is request "help" to the command.
            We should provide enough information to the user so she/he
            can use the software.
      Given a command shell
      When I execute "geoffrey --help"
      Then I can see "usage: geoffrey" in "stdout"
      And the command return value is "0"
