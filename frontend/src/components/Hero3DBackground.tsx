import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

export const Hero3DBackground = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleMouseMove = (e: MouseEvent) => {
      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;
      
      const x = (clientX / innerWidth - 0.5) * 20;
      const y = (clientY / innerHeight - 0.5) * 20;
      
      container.style.setProperty('--mouse-x', `${x}deg`);
      container.style.setProperty('--mouse-y', `${y}deg`);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div 
      ref={containerRef}
      className="absolute inset-0 overflow-hidden"
      style={{ perspective: '1000px' }}
    >
      {/* 3D Grid */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(to right, hsl(var(--neon-purple) / 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, hsl(var(--neon-purple) / 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
          transform: 'rotateX(var(--mouse-y, 0deg)) rotateY(var(--mouse-x, 0deg))',
          transformOrigin: 'center center',
          transition: 'transform 0.1s ease-out',
        }}
      />

      {/* Orbiting Rings */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
          className="absolute w-[500px] h-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-neon-purple/20"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
          className="absolute w-[700px] h-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-neon-blue/15"
          style={{ transform: 'rotateX(60deg)' }}
        />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 50, repeat: Infinity, ease: 'linear' }}
          className="absolute w-[900px] h-[900px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-neon-pink/10"
          style={{ transform: 'rotateX(75deg) rotateY(10deg)' }}
        />
      </div>

      {/* Floating Particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-neon-purple/60"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.8, 0.2],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* 3D Geometric Shapes */}
      <motion.div
        animate={{ 
          rotateX: [0, 360],
          rotateY: [0, 360],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        className="absolute top-20 right-20 w-20 h-20 opacity-30"
        style={{ transformStyle: 'preserve-3d' }}
      >
        <div className="absolute inset-0 border-2 border-neon-purple/40 transform rotateY-45" />
        <div className="absolute inset-0 border-2 border-neon-blue/40 transform rotate-45" />
      </motion.div>

      <motion.div
        animate={{ 
          rotateZ: [0, 360],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
        className="absolute bottom-40 left-20 w-16 h-16 opacity-20 border-2 border-neon-pink/40 rounded-lg"
      />
    </div>
  );
};
