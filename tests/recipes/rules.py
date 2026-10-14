"""The starter pack's rules as the pure `Ruleset` the categorizer reads."""

from scaffolding.service.domain.expenses.calc import Rule, Ruleset
from scaffolding.service.domain.setup import use_cases as setup


def starter_rules() -> Ruleset:
    pack = setup.starter()
    return Ruleset(
        debit=tuple(Rule(rule.pattern, rule.category) for rule in pack.debit_rules),
        credit=tuple(Rule(rule.pattern, rule.category) for rule in pack.credit_rules),
    )


STARTER = starter_rules()
