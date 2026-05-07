import { motion } from "framer-motion";

export default function LoadingScreen() {
  return (
    <div className="w-screen h-screen flex flex-col bg-neutral-900 justify-center items-center gap-8">
      <motion.div
        initial={{ rotate: 0 }}
        animate={{
          rotate: [0, 15, -15, 0, 360],
          scale: [1, 1.1, 1],
        }}
        transition={{
          rotate: {
            repeat: Infinity,
            duration: 1.5,
            ease: "linear",
          },
          scale: {
            repeat: Infinity,
            duration: 0.8,
            ease: "easeInOut",
          },
        }}
        style={{ width: 80, height: 80 }}
      >
        <svg viewBox="0 0 100 100" className="w-full h-full drop-shadow-lg">
          <circle cx="50" cy="50" r="48" fill="#f00" stroke="#333" strokeWidth="4" />
          <rect x="2" y="46" width="96" height="8" fill="#333" />
          <circle cx="50" cy="50" r="14" fill="#fff" stroke="#333" strokeWidth="3" />
          <circle cx="50" cy="50" r="8" fill="#333" />
          <circle cx="54" cy="46" r="3" fill="#fff" opacity="0.6" />
          <path d="M 2 50 A 48 48 0 0 1 98 50" fill="none" stroke="#333" strokeWidth="4" />
        </svg>
      </motion.div>

      <motion.p
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
        className="text-white text-body font-bold tracking-wide"
      >
        Preparando el combate
      </motion.p>
    </div>
  );
}