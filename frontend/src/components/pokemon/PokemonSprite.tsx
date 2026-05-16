interface PokemonSpriteProps {
  name?: string;
  sprite: string | undefined;
  instanceId?: string;
  instanceIds?: string[];
  trainerId?: string;
  direction?: 'left' | 'right';
  isFainted?: boolean;
}

export default function PokemonSprite(props: PokemonSpriteProps) {
  return (
    <div className="relative z-50">
      <img
        className="relative inline-block h-fit"
        style={{
          transform: 'scale(2)',
          transformOrigin: 'center bottom',
          zIndex: 50,
          opacity: props.isFainted ? 0.5 : 1,
        }}
        src={props.sprite}
        alt={props.name}
      />
    </div>
  );
}