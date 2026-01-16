import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Target, BarChart3, BadgeCheck, Brain } from 'lucide-react';

const features = [
  {
    icon: Target,
    title: 'Placement Readiness Score',
    description: 'AI-powered assessment of your skills, resume, and interview readiness with personalized improvement suggestions.',
    gradient: 'from-neon-purple via-neon-blue to-neon-purple',
  },
  {
    icon: BarChart3,
    title: 'Real-Time Application Tracking',
    description: 'Monitor every application status from applied to offer. Never miss an update or deadline again.',
    gradient: 'from-neon-blue via-neon-pink to-neon-blue',
  },
  {
    icon: BadgeCheck,
    title: 'Verified Internship System',
    description: 'Only verified companies and opportunities. Every listing is TPO-approved and alumnireviewed.',
    gradient: 'from-neon-pink via-neon-purple to-neon-pink',
  },
  {
    icon: Brain,
    title: 'AI Resume Analyzer',
    description: 'Get instant feedback on your resume with ATS compatibility scores and keyword optimization tips.',
    gradient: 'from-emerald-400 via-cyan-400 to-emerald-400',
  },
];

export const FeaturesSection = () => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' });

  return (
    <section id="features" ref={sectionRef} className="py-32 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 section-gradient" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-neon-purple/5 rounded-full blur-[150px]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <span className="text-primary text-sm font-semibold uppercase tracking-widest mb-4 block">
            Features
          </span>
          <h2 className="font-display text-4xl md:text-6xl font-bold text-foreground mb-6">
            Everything You Need to
            <br />
            <span className="gradient-text">Land Your Dream Role</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            A complete toolkit designed to streamline your placement journey from start to finish.
          </p>
        </motion.div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {features.map((feature, index) => (
            <FeatureCard 
              key={feature.title} 
              feature={feature} 
              index={index}
              isInView={isInView}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

interface FeatureCardProps {
  feature: typeof features[0];
  index: number;
  isInView: boolean;
}

const FeatureCard = ({ feature, index, isInView }: FeatureCardProps) => {
  const Icon = feature.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, rotateX: -15 }}
      animate={isInView ? { opacity: 1, y: 0, rotateX: 0 } : {}}
      transition={{ duration: 0.8, delay: index * 0.15 }}
      className="group perspective-1000"
    >
      <div 
        className="relative glass-card-glow p-8 h-full overflow-hidden transition-all duration-500 group-hover:scale-[1.02]"
        style={{ transformStyle: 'preserve-3d' }}
      >
        {/* Animated gradient border */}
        <div 
          className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
          style={{
            background: `linear-gradient(135deg, ${feature.gradient.split(' ').filter(c => c.startsWith('from-') || c.startsWith('via-') || c.startsWith('to-')).map(c => {
              const color = c.replace('from-', '').replace('via-', '').replace('to-', '');
              return `hsl(var(--${color}))`;
            }).join(', ')})`,
            padding: '2px',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            maskComposite: 'exclude',
          }}
        />

        {/* Icon */}
        <motion.div
          whileHover={{ rotateY: 360, scale: 1.1 }}
          transition={{ duration: 0.6 }}
          className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 shadow-lg`}
          style={{ 
            boxShadow: '0 10px 40px -10px hsl(var(--neon-purple) / 0.4)',
          }}
        >
          <Icon className="w-8 h-8 text-foreground" />
        </motion.div>

        {/* Content */}
        <h3 className="font-display text-2xl font-bold text-foreground mb-4 group-hover:text-primary transition-colors">
          {feature.title}
        </h3>
        <p className="text-muted-foreground leading-relaxed">
          {feature.description}
        </p>

        {/* Hover glow effect */}
        <div className="absolute -bottom-20 -right-20 w-40 h-40 bg-primary/20 rounded-full blur-[60px] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      </div>
    </motion.div>
  );
};
