interface PokemonMOvementProps {
  name: string;
  type: string;
  currentPP: number;
  maxPP: number;
  bg?: string;
}

export default function PokemonMovement(props: PokemonMOvementProps) {
  return (
    <div
      style={{
        backgroundColor: props.bg,
      }}
      className="flex flex-col bg-slate-400 items-center rounded-lg gap-6 border-3 border-black px-4 py-3"
    >
      <p className="text-body/[12px]">{props.name}</p>
      <div className="flex flex-1 justify-between gap-12">
        <p className="text-small/[8px]">{props.type}</p>
        <p className="text-small/[8px]">
          {props.currentPP}/{props.maxPP}
        </p>
      </div>
    </div>
  );
}
