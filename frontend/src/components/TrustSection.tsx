import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Building2, Shield, Users } from 'lucide-react';

const badges = [
  {
    icon: Building2,
    title: 'Verified Companies',
    description: '500+ verified employers',
    gradient: 'from-neon-purple to-neon-blue',
  },
  {
    icon: Shield,
    title: 'TPO Approved',
    description: 'Trusted by 200+ colleges',
    gradient: 'from-neon-blue to-neon-pink',
  },
  {
    icon: Users,
    title: 'Alumni Reviewed',
    description: 'Real feedback from alumni',
    gradient: 'from-neon-pink to-neon-purple',
  },
];

export const TrustSection = () => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' });

  return (
    <section ref={sectionRef} className="py-24 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 section-gradient" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <span className="text-primary text-sm font-semibold uppercase tracking-widest mb-4 block">
            Trusted Platform
          </span>
          <h2 className="font-display text-4xl md:text-5xl font-bold text-foreground mb-6">
            Built on Trust &
            <span className="gradient-text"> Verification</span>
          </h2>
        </motion.div>

        {/* Trust Badges */}
        <div className="flex flex-wrap justify-center gap-8 max-w-4xl mx-auto">
          {badges.map((badge, index) => {
            const Icon = badge.icon;

            return (
              <motion.div
                key={badge.title}
                initial={{ opacity: 0, y: 40 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="group"
              >
                <div className="glass-card-glow px-8 py-6 flex items-center gap-4 neon-border">
                  <motion.div
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                    className={`w-14 h-14 rounded-xl bg-gradient-to-br ${badge.gradient} flex items-center justify-center shadow-lg`}
                  >
                    <Icon className="w-7 h-7 text-foreground" />
                  </motion.div>
                  <div>
                    <h3 className="font-display text-xl font-bold text-foreground group-hover:text-primary transition-colors">
                      {badge.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">{badge.description}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Company Logos */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-16"
        >
          <p className="text-center text-muted-foreground text-sm mb-8">
            Trusted by students placed at
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12 opacity-50">
            {['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix'].map((company) => (
              <motion.div
                key={company}
                whileHover={{ scale: 1.1, opacity: 1 }}
                className="font-display text-xl md:text-2xl font-bold text-muted-foreground/60 hover:text-foreground transition-all cursor-pointer"
              >
                {company}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};
