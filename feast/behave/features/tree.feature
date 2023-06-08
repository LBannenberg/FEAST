Feature: Inflating and deflating trees

  Scenario Outline: inflating and deflating a tree from a recipe
    Given a recipe <recipe>
    When we inflate a tree from that recipe
    Then the deflate is equal to the recipe
    Examples: Recipes
      | recipe                                                                                |
      | numeric:1                                                                             |
      | numeric:0                                                                             |
      | boolean_expression:not\|boolean_expression:not\|boolean_expression:truthy\|numeric:-1 |

  Scenario Outline: trees evaluate correctly
    Given a recipe <recipe>
    When we inflate a tree from that recipe
    Then it evaluates to to the correct result: <result>
    Examples:
      | recipe                                                                          | result |
      | numeric:1                                                                       | 1      |
      | numeric:0                                                                       | 0      |
      | boolean:false                                                                   | false  |
      | boolean:true                                                                    | true   |
      | boolean_expression:not\|boolean:true                                            | false  |
      | numeric_expression:negative\|numeric:2                                          | -2     |
      | boolean_expression:<\|numeric:3\|numeric_expression:-\|numeric:0.5\|numeric:0.5 | false  |

  Scenario Outline: trees calculate their height correctly
    Given a recipe <recipe>
    When we inflate a tree from that recipe
    Then it reports the correct height: <height>
    Examples:
      | recipe                                                                                | height |
      | numeric:1                                                                             | 1      |
      | numeric:0                                                                             | 1      |
      | boolean:false                                                                         | 1      |
      | boolean:true                                                                          | 1      |
      | boolean_expression:not\|boolean:true                                                  | 2      |
      | numeric_expression:negative\|numeric:2                                                | 2      |
      | boolean_expression:not\|boolean_expression:not\|boolean_expression:truthy\|numeric:-1 | 4      |
      | boolean_expression:<\|numeric:3\|numeric_expression:-\|numeric:0.5\|numeric:0.5       | 3      |
