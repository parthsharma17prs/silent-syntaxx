import { motion } from 'framer-motion';
import { Briefcase, TrendingUp, Calendar, Award } from 'lucide-react';

const cards = [
  {
    icon: Briefcase,
    title: 'Applications',
    value: '24',
    trend: '+5 this week',
    color: 'from-neon-purple to-neon-blue',
  },
  {
    icon: TrendingUp,
    title: 'Shortlisted',
    value: '8',
    trend: '33% rate',
    color: 'from-neon-blue to-neon-pink',
  },
  {
    icon: Calendar,
    title: 'Interviews',
    value: '3',
    trend: 'Next: Monday',
    color: 'from-neon-pink to-neon-purple',
  },
  {
    icon: Award,
    title: 'Offers',
    value: '2',
    trend: '₹12L avg CTC',
    color: 'from-green-500 to-emerald-400',
  },
];

export const FloatingCards = () => {
  return (
    <>
      {/* Top Left Card */}
      <motion.div
        initial={{ opacity: 0, x: -100, y: -50 }}
        animate={{ opacity: 1, x: 0, y: 0 }}
        transition={{ duration: 1, delay: 0.5 }}
        className="absolute top-32 left-10 lg:left-20 hidden lg:block"
      >
        <motion.div
          animate={{ y: [0, -15, 0], rotate: [-2, 2, -2] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
          className="glass-card-glow p-5 w-48 neon-border"
        >
          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${cards[0].color} flex items-center justify-center mb-3`}>
            <Briefcase className="w-5 h-5 text-foreground" />
          </div>
          <div className="text-sm text-muted-foreground mb-1">{cards[0].title}</div>
          <div className="font-display text-3xl font-bold text-foreground">{cards[0].value}</div>
          <div className="text-xs text-primary mt-1">{cards[0].trend}</div>
        </motion.div>
      </motion.div>

      {/* Top Right Card */}
      <motion.div
        initial={{ opacity: 0, x: 100, y: -50 }}
        animate={{ opacity: 1, x: 0, y: 0 }}
        transition={{ duration: 1, delay: 0.7 }}
        className="absolute top-48 right-10 lg:right-24 hidden lg:block"
      >
        <motion.div
          animate={{ y: [0, -12, 0], rotate: [2, -2, 2] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
          className="glass-card-glow p-5 w-48 neon-border"
        >
          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${cards[1].color} flex items-center justify-center mb-3`}>
            <TrendingUp className="w-5 h-5 text-foreground" />
          </div>
          <div className="text-sm text-muted-foreground mb-1">{cards[1].title}</div>
          <div className="font-display text-3xl font-bold text-foreground">{cards[1].value}</div>
          <div className="text-xs text-primary mt-1">{cards[1].trend}</div>
        </motion.div>
      </motion.div>

      {/* Bottom Left Card */}
      <motion.div
        initial={{ opacity: 0, x: -100, y: 50 }}
        animate={{ opacity: 1, x: 0, y: 0 }}
        transition={{ duration: 1, delay: 0.9 }}
        className="absolute bottom-48 left-16 lg:left-32 hidden lg:block"
      >
        <motion.div
          animate={{ y: [0, -10, 0], rotate: [-1, 1, -1] }}
          transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
          className="glass-card-glow p-5 w-48 neon-border"
        >
          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${cards[2].color} flex items-center justify-center mb-3`}>
            <Calendar className="w-5 h-5 text-foreground" />
          </div>
          <div className="text-sm text-muted-foreground mb-1">{cards[2].title}</div>
          <div className="font-display text-3xl font-bold text-foreground">{cards[2].value}</div>
          <div className="text-xs text-primary mt-1">{cards[2].trend}</div>
        </motion.div>
      </motion.div>

      {/* Bottom Right Card */}
      <motion.div
        initial={{ opacity: 0, x: 100, y: 50 }}
        animate={{ opacity: 1, x: 0, y: 0 }}
        transition={{ duration: 1, delay: 1.1 }}
        className="absolute bottom-32 right-20 lg:right-40 hidden lg:block"
      >
        <motion.div
          animate={{ y: [0, -18, 0], rotate: [1, -1, 1] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut', delay: 1.5 }}
          className="glass-card-glow p-5 w-48 neon-border"
        >
          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${cards[3].color} flex items-center justify-center mb-3`}>
            <Award className="w-5 h-5 text-foreground" />
          </div>
          <div className="text-sm text-muted-foreground mb-1">{cards[3].title}</div>
          <div className="font-display text-3xl font-bold text-foreground">{cards[3].value}</div>
          <div className="text-xs text-emerald-400 mt-1">{cards[3].trend}</div>
        </motion.div>
      </motion.div>
    </>
  );
};
