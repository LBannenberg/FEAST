Feature: Inflating and deflating trees

  Scenario Outline: inflating and deflating a tree from a recipe
    Given a recipe <recipe>
    When we inflate a tree from that recipe
    Then the deflate is equal to the recipe
    Examples: Recipes
      | recipe                                                                             |
      | numeric_nullary:1                                                                  |
      | numeric_nullary:0                                                                  |
      | boolean_unary:not\|boolean_unary:not\|boolean_unary_num:truthy\|numeric_nullary:-1 |

  Scenario Outline: trees evaluate correctly
    Given a recipe <recipe>
    When we inflate a tree from that recipe
    Then it evaluates to to the correct result: <result>
    Examples:
      | recipe                                                                                              | result |
      | numeric_nullary:1                                                                                   | 1      |
      | numeric_nullary:0                                                                                   | 0      |
      | boolean_nullary:false                                                                               | false  |
      | boolean_nullary:true                                                                                | true   |
      | boolean_unary:not\|boolean_nullary:true                                                             | false  |
      | numeric_unary:negative\|numeric_nullary:2                                                           | -2     |
      | boolean_binary_num:<\|numeric_nullary:3\|numeric_binary:-\|numeric_nullary:0.5\|numeric_nullary:0.5 | false  |

  Scenario Outline: trees calculate their height correctly
    Given a recipe <recipe>
    When we inflate a tree from that recipe
    Then it reports the correct height: <height>
    Examples:
      | recipe                                                                                              | height |
      | numeric_nullary:1                                                                                   | 1      |
      | numeric_nullary:0                                                                                   | 1      |
      | boolean_nullary:false                                                                               | 1      |
      | boolean_nullary:true                                                                                | 1      |
      | boolean_unary:not\|boolean_nullary:true                                                             | 2      |
      | numeric_unary:negative\|numeric_nullary:2                                                           | 2      |
      | boolean_unary:not\|boolean_unary:not\|boolean_unary_num:truthy\|numeric_nullary:-1                  | 4      |
      | boolean_binary_num:<\|numeric_nullary:3\|numeric_binary:-\|numeric_nullary:0.5\|numeric_nullary:0.5 | 3      |
