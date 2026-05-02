"""Strategy for `proxy_hp` condition effects."""

from .pending import PendingConditionEffectStrategy


class ProxyHpConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "proxy_hp"
    hook = "modify_damage"
