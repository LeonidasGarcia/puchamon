import { useRef, useState } from 'react';

interface PokemonProps {
  name: string;
  sprite: string | undefined;
}

// TODO Solucionar el problema del rescalado multiplicativo y el rescalado incorrecto (no necesario)
export default function MiniPokemonSprite(
  props: PokemonProps & React.HTMLAttributes<HTMLImageElement>,
) {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const imgRef = useRef<HTMLImageElement | null>(null);

  const RESCALING_CONSTANT = 0.7;

  const onLoad = () => {
    if (imgRef.current) {
      const naturalWidth = imgRef.current.width;
      const naturalHeight = imgRef.current.height;

      setDimensions({
        width: naturalWidth * RESCALING_CONSTANT,
        height: naturalHeight * RESCALING_CONSTANT,
      });
    }
  };

  return (
    <img
      className={`inline ${props.className}`}
      style={{
        width: dimensions.width ? `${dimensions.width}px` : 'auto',
        height: dimensions.height ? `${dimensions.height}px` : 'auto',
      }}
      onLoad={onLoad}
      src={props.sprite}
      alt={props.name}
      ref={imgRef}
    />
  );
}
