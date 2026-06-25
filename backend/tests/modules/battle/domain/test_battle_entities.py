"""Tests for battle domain entity validation."""

from puchamon.modules.battle.domain.entities import Player


def test_player_accepts_hard_ga_ai_level():
    player = Player(trainer_id="ai", name="AI", controller_type="ai", ai_level=4)

    assert player.ai_level == 4
