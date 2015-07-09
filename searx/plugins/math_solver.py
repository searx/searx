'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2015 by Thomas Pointhuber
'''
from flask.ext.babel import gettext
from sympy import simplify, solve, Symbol, count_ops, S
from sympy.printing.mathml import mathml
from sympy.utilities.mathml import c2p
from sympy.parsing.sympy_tokenize import NAME, OP
from sympy.parsing.sympy_parser import (auto_symbol,
                                        auto_number,
                                        implicit_application,
                                        convert_xor,
                                        factorial_notation,
                                        parse_expr,
                                        function_exponentiation)
import re


name = "Math Solver"
description = gettext('calculate mathematic equations if possible, using sympy')
default_on = True


# regular expression to detect special mathematic equations
regex_integral = re.compile(r"(integral(\s+of)?|integrate)\s+(?P<equation>.+)\s+d(?P<variable>[a-z])", re.IGNORECASE)


def transform_equals_sign(tokens, local_dict, global_dict):
    """Transforms the equals sign ``=`` to instances of Eq.

    Source: https://github.com/sympy/sympy/pull/9255

    """
    result = []
    if (OP, "=") in tokens:
        result.append((NAME, "Eq"))
        result.append((OP, "("))
        for index, token in enumerate(tokens):
            if token == (OP, "="):
                result.append((OP, ","))
                continue
            result.append(token)
        result.append((OP, ")"))
    else:
        result = tokens
    return result


# transformations which should be used in all parse_expr
default_transformations = (auto_number,
                           auto_symbol,
                           factorial_notation,
                           implicit_application,
                           function_exponentiation,
                           convert_xor)
# transformations which are used when parsing the whole query
searx_transformations = (default_transformations + (
                         transform_equals_sign,))
# transformations which are used when parsing an integral
integral_transformations = (default_transformations)


def formate_equation(equation):
    ''' convert equation to formated Presentation MathML '''
    equation_html = c2p(mathml(equation))

    # convert inivisible times into visible times
    equation_html = equation_html.replace('&#x2062;', '&#x22C5;')

    # TODO: formate equation
    return '<p style="font-size: 25px;">{0}</p>'.format(equation_html)


def formate_equal_equations(equations):
    ''' convert equations with are equal to formated Presentation MathML '''
    equation_mathml = "<apply><eq/>"
    for eqation in equations:
        equation_mathml += mathml(eqation)
    equation_mathml += "</apply>"

    # convert to Presentation MathML
    equation_html = c2p(equation_mathml)

    # convert inivisible times into visible times
    equation_html = equation_html.replace('&#x2062;', '&#x22C5;')

    # TODO: formate equation
    return '<p style="font-size: 25px;">{0}</p>'.format(equation_html)


# attach callback to the post search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def post_search(request, ctx):
    try:
        ''' test if whole query is valide expression and calculate it

            example querys:
                * 2+3/5
                * sin 3
                * sin(pi)
        '''
        equation = parse_expr(ctx['search'].query,
                              transformations=searx_transformations,
                              evaluate=False)

        # variables could be only single characters (to differ between equations and normal queries)
        var_symbols = equation.atoms(Symbol)
        for var in var_symbols:
            if len(str(var)) != 1:
                raise Exception('no equation')

        equation_simplify = simplify(equation)

        # simple calculation with no variables
        if len(var_symbols) == 0:
            # check if equation is simplified
            if count_ops(equation_simplify) != count_ops(equation):
                # show simplification of equation
                equal_results = [equation, equation_simplify]

                # calculate result if required
                if count_ops(equation_simplify) >= 1:
                    # TODO: removing trailing zeros
                    equal_results.append(S(equation_simplify.evalf(chop=True)))

                # create answere and cleare exising one
                ctx['search'].answers = [{'content_raw': formate_equal_equations(equal_results),
                                          'label': 'sympy'}]
                return True

            # check if equation is not already a single number
            elif count_ops(equation_simplify) >= 1:
                # calculate result
                # TODO: removing trailing zeros
                result_float = S(equation_simplify.evalf(chop=True))

                # create answere and cleare exising one
                ctx['search'].answers = [{'content_raw': formate_equal_equations([equation_simplify, result_float]),
                                          'label': 'sympy'}]
                return True

        # calculation with variables
        else:
            # check if we can use a solve
            if len(var_symbols) == 1 and ctx['search'].query.count("=") == 1:
                solve_equation = solve(equation, list(var_symbols)[0])

                # better formating if there is only one result
                single_result = False
                if len(solve_equation) == 1:
                    solve_equation = solve_equation[0]
                    single_result = True

                equal_results = [list(var_symbols)[0], solve_equation]

                # calculate result if possible and required
                if single_result and count_ops(solve_equation) >= 1:
                    # TODO: removing trailing zeros
                    equal_results.append(S(solve_equation.evalf(chop=True)))

                result_html = formate_equation(equation_simplify)
                result_html += formate_equal_equations(equal_results)

                # create answere and cleare exising one
                ctx['search'].answers = [{'content_raw': result_html,
                                          'label': 'sympy'}]
                return True
            # TODO: detect equation which could be ploted (x|y)
            else:
                # check if equation is simplified
                if count_ops(equation_simplify) != count_ops(equation):
                    # create answere and cleare exising one
                    ctx['search'].answers = [{'content_raw': formate_equal_equations([equation, equation_simplify]),
                                              'label': 'sympy'}]
                else:
                    # create answere and cleare exising one
                    ctx['search'].answers = [{'content_raw': formate_equation(equation_simplify),
                                              'label': 'sympy'}]
                return True

    except Exception, e:
        print str(e)

    if regex_integral.match(ctx['search'].query):
        ''' Solve integral equations

            example querys:
                * integrate sin(x) dx
                * integral of cos(x) dx
                * integral e**2 dx
        '''
        integral_equation = regex_integral.match(ctx['search'].query).groupdict()

        try:
            # create equation which is representing the search-query
            equation_string = "Integral({0}, {1})".format(integral_equation['equation'],
                                                          integral_equation['variable'])
            equation = parse_expr(equation_string,
                                  transformations=integral_transformations,
                                  evaluate=False)

            # calculate equation
            equation_solved_string = "integrate({0}, {1})".format(integral_equation['equation'],
                                                                  integral_equation['variable'])
            equation_solved = parse_expr(equation_solved_string,
                                         transformations=integral_transformations,
                                         evaluate=True)

            # create answere and cleare exising one
            ctx['search'].answers = [{'content_raw': formate_equal_equations([equation, equation_solved]),
                                      'label': 'sympy'}]
            return True
        except:
            pass

    return True
