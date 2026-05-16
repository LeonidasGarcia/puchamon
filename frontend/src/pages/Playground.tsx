import { motion, type Variants } from 'framer-motion';

export default function Playground() {
  return (
    <div className="flex items-center justify-center h-screen">
      <span className="text-black text-h1">Playground</span>
      <div>
        <SequentialList />
      </div>
    </div>
  );
}

// 1. Definimos las variantes del contenedor padre
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      // Espera 0.5s antes de iniciar la secuencia
      delayChildren: 0.5,
      // Cada hijo aparecerá con 0.3s de diferencia respecto al anterior
      staggerChildren: 0.3,
    },
  },
};

// 2. Definimos las variantes de cada elemento hijo
const itemVariants: Variants = {
  hidden: {
    opacity: 0,
    x: -20,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      type: 'spring',
      stiffness: 120,
    },
  },
};

export const SequentialList = () => {
  const items = [
    'Cargando módulos...',
    'Verificando base de datos...',
    'Estableciendo conexión...',
    'Listo!',
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{ listStyle: 'none', padding: 0 }}
    >
      {items.map((text, index) => (
        <motion.p
          key={index}
          variants={itemVariants}
          style={{
            margin: '10px 0',
            padding: '15px',
            background: '#f0f0f0',
            borderRadius: '8px',
            fontFamily: 'sans-serif',
          }}
        >
          {text}
        </motion.p>
      ))}
    </motion.div>
  );
};
