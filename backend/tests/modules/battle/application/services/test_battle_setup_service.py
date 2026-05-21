import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from puchamon.modules.battle.application.services.battle_setup_service import BattleSetupService
from puchamon.modules.battle.domain.entities import Player, BattleInstance, Battle
from puchamon.modules.pokedex.domain.entities import Pokemon, Moveset, Movement
from puchamon.modules.pokedex.domain.entities.pokemons import BaseStats


@pytest.fixture
def mock_moveset():
    # Use model_construct to avoid validation and DB initialization
    return Moveset.model_construct(
        id=str(ObjectId()),
        pokemon_id="pikachu",
        moveset_name="Pikachu Set",
        moves=["tackle", "thunder-shock"],
        ability="static",
        item="light-ball",
        nature="Hardy",
        evs={},
    )


@pytest.fixture
def mock_pokemon():
    return Pokemon.model_construct(
        id="pikachu",
        name="Pikachu",
        types=["electric"],
        base_stats=BaseStats(hp=35, atk=55, def_=40, spa=50, spd=50, spe=90),
        abilities=["static"],
    )


@pytest.fixture
def mock_movement():
    return Movement.model_construct(
        id="tackle",
        name="Tackle",
        pp=35,
        priority=0,
        effect_ids=[],
    )


@pytest.mark.asyncio
async def test_create_battle_successfully(mock_pokemon, mock_moveset, mock_movement):
    players = [
        Player(trainer_id="t1", name="Ash", controller_type="human"),
        Player(trainer_id="t2", name="Gary", controller_type="ai"),
    ]

    mock_battle = Battle.model_construct(id="b1", turn=1, players=players)
    mock_instance_t1 = BattleInstance.model_construct(id="inst1", trainer_id="t1", pokemon_id="pikachu", fainted=False)
    mock_instance_t2 = BattleInstance.model_construct(id="inst2", trainer_id="t2", pokemon_id="pikachu", fainted=False)

    with patch("puchamon.modules.battle.application.services.battle_setup_service.Battle", return_value=mock_battle), \
         patch.object(BattleSetupService, "_generate_random_pokemon") as mock_gen:
        
        mock_gen.side_effect = [mock_instance_t1, mock_instance_t2]
        
        battle, instances = await BattleSetupService.create_battle(
            battle_type="1v1",
            players=players,
            team_size=1,
            movements={},
        )

        assert battle.id == "b1"
        assert len(instances) == 2
        assert instances[0].trainer_id == "t1"
        assert instances[1].trainer_id == "t2"


@pytest.mark.asyncio
async def test_generate_random_pokemon_orchestration(mock_pokemon, mock_moveset, mock_movement):
    movements = {"tackle": mock_movement}
    
    mock_instance = BattleInstance.model_construct(id="inst1", trainer_id="t1", pokemon_id="pikachu")

    # Mock EVERYTHING to avoid any side effects from Beanie/Pydantic
    with patch("puchamon.modules.battle.application.services.battle_setup_service.Moveset") as mock_moveset_cls, \
         patch("puchamon.modules.battle.application.services.battle_setup_service.Pokemon") as mock_pokemon_cls, \
         patch("puchamon.modules.battle.application.services.battle_setup_service.BattleInstance", return_value=mock_instance):
        
        mock_agg_cursor = AsyncMock()
        mock_agg_cursor.to_list.return_value = [{"some": "data"}]
        mock_moveset_cls.aggregate.return_value = mock_agg_cursor
        mock_moveset_cls.return_value = mock_moveset
        
        mock_pokemon_cls.get = AsyncMock(return_value=mock_pokemon)

        instance = await BattleSetupService._generate_random_pokemon(
            battle_id="b1",
            trainer_id="t1",
            slot=0,
            movements=movements,
            move_effects={},
        )

        assert instance.id == "inst1"
        assert instance.pokemon_id == "pikachu"


def test_filter_valid_moves():
    with patch.object(BattleSetupService, "_is_move_implemented") as mock_impl:
        mock_impl.side_effect = lambda mid, m, e: mid == "tackle"
        
        move_ids = ["tackle", "unimplemented-move"]
        valid_moves = BattleSetupService._filter_valid_moves(move_ids, {}, {})
        
        assert valid_moves == ["tackle"]
