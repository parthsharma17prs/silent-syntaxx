import { useRef, useEffect, useState } from 'react';
import { motion, useInView, useSpring, useTransform } from 'framer-motion';
import { TrendingUp, Users, Calendar, Award } from 'lucide-react';

const stats = [
  { icon: Users, label: 'Applications Applied', value: 247, suffix: '' },
  { icon: TrendingUp, label: 'Shortlisted', value: 89, suffix: '' },
  { icon: Calendar, label: 'Interviews Scheduled', value: 34, suffix: '' },
  { icon: Award, label: 'Offers Received', value: 12, suffix: '' },
];

const AnimatedNumber = ({ value, isInView }: { value: number; isInView: boolean }) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (isInView) {
      const duration = 2000;
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        setDisplayValue(Math.floor(value * easeOut));
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      
      animate();
    }
  }, [value, isInView]);

  return <span>{displayValue}</span>;
};

export const DashboardPreview = () => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' });

  return (
    <section id="dashboard" ref={sectionRef} className="py-32 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-neon-blue/10 rounded-full blur-[150px]" />
      <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-neon-purple/10 rounded-full blur-[120px]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <span className="text-primary text-sm font-semibold uppercase tracking-widest mb-4 block">
            Dashboard
          </span>
          <h2 className="font-display text-4xl md:text-6xl font-bold text-foreground mb-6">
            Your Career at a
            <span className="gradient-text"> Glance</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Real-time insights and analytics to keep you ahead in your placement journey.
          </p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12"
        >
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={isInView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                className="glass-card-glow p-6 text-center group hover:scale-105 transition-transform duration-300"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-neon-purple to-neon-blue flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <Icon className="w-6 h-6 text-foreground" />
                </div>
                <div className="font-display text-4xl md:text-5xl font-bold text-foreground mb-2">
                  <AnimatedNumber value={stat.value} isInView={isInView} />
                  {stat.suffix}
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Dashboard Preview Card */}
        <motion.div
          initial={{ opacity: 0, y: 80, rotateX: 10 }}
          animate={isInView ? { opacity: 1, y: 0, rotateX: 0 } : {}}
          transition={{ duration: 1, delay: 0.4 }}
          className="max-w-5xl mx-auto"
        >
          <div className="glass-card-glow p-8 relative overflow-hidden">
            {/* Neon border glow */}
            <div className="absolute inset-0 rounded-2xl neon-border" />
            
            {/* Dashboard Header */}
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-border/50">
              <div>
                <h3 className="font-display text-2xl font-bold text-foreground">
                  Welcome back, Alex 👋
                </h3>
                <p className="text-muted-foreground mt-1">
                  You have 3 interviews this week. Keep it up!
                </p>
              </div>
              <div className="hidden md:flex items-center gap-3">
                <div className="px-4 py-2 rounded-full bg-green-500/20 border border-green-500/30 text-green-400 text-sm font-medium">
                  On Track
                </div>
              </div>
            </div>

            {/* Progress Chart Mock */}
            <div className="grid md:grid-cols-3 gap-6">
              {/* Activity Chart */}
              <div className="md:col-span-2 p-6 rounded-xl bg-card/50 border border-border/30">
                <h4 className="text-sm font-medium text-muted-foreground mb-4">Weekly Activity</h4>
                <div className="flex items-end gap-2 h-32">
                  {[40, 65, 45, 80, 55, 90, 70].map((height, i) => (
                    <motion.div
                      key={i}
                      initial={{ height: 0 }}
                      animate={isInView ? { height: `${height}%` } : {}}
                      transition={{ duration: 0.8, delay: 0.6 + i * 0.1 }}
                      className="flex-1 rounded-t-lg bg-gradient-to-t from-neon-purple to-neon-blue"
                    />
                  ))}
                </div>
                <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                    <span key={day}>{day}</span>
                  ))}
                </div>
              </div>

              {/* Quick Stats */}
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-card/50 border border-border/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Profile Strength</span>
                    <span className="text-sm font-bold text-primary">85%</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={isInView ? { width: '85%' } : {}}
                      transition={{ duration: 1, delay: 0.8 }}
                      className="h-full rounded-full bg-gradient-to-r from-neon-purple to-neon-blue"
                    />
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-card/50 border border-border/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Resume Score</span>
                    <span className="text-sm font-bold text-green-400">92%</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={isInView ? { width: '92%' } : {}}
                      transition={{ duration: 1, delay: 0.9 }}
                      className="h-full rounded-full bg-gradient-to-r from-green-500 to-emerald-400"
                    />
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-card/50 border border-border/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Interview Ready</span>
                    <span className="text-sm font-bold text-neon-pink">78%</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={isInView ? { width: '78%' } : {}}
                      transition={{ duration: 1, delay: 1 }}
                      className="h-full rounded-full bg-gradient-to-r from-neon-pink to-neon-purple"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
