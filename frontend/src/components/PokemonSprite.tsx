import { useRef, useState } from "react";

const RESCALING_CONSTANT = 2;

interface PokemonProps {
  name?: string;
  sprite: string | undefined;
}

// TODO Solucionar el problema del rescalado multiplicativo y el rescalado incorrecto al cambiar de cara (no necesario)
export default function PokemonSprite(props: PokemonProps) {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  const imgRef = useRef<HTMLImageElement | null>(null);

  const onLoad = () => {
    if (imgRef.current) {
      const naturalWidth = imgRef.current.width;
      const naturalHeight = imgRef.current.height;

      console.log(naturalWidth, naturalHeight);

      setDimensions({
        width: naturalWidth * RESCALING_CONSTANT,
        height: naturalHeight * RESCALING_CONSTANT,
      });
    }
  };

  return (
    <img
      className="inline-block h-fit z-50"
      style={{
        width: dimensions.width ? `${dimensions.width}px` : "",
        height: dimensions.height ? `${dimensions.height}px` : "",
      }}
      onLoad={onLoad}
      src={props.sprite}
      alt={props.name}
      ref={imgRef}
    />
  );
}
