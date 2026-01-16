import { useRef } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { UserCircle, Target, LineChart, Trophy } from 'lucide-react';

const steps = [
  {
    icon: UserCircle,
    title: 'Build Your Profile',
    description: 'Create a comprehensive profile showcasing your skills, projects, and achievements. Our AI helps optimize it for maximum visibility.',
    color: 'from-neon-purple to-neon-blue',
  },
  {
    icon: Target,
    title: 'Apply Smartly',
    description: 'Get personalized job recommendations based on your profile. Apply with one click to verified opportunities.',
    color: 'from-neon-blue to-neon-pink',
  },
  {
    icon: LineChart,
    title: 'Track Progress',
    description: 'Monitor every application in real-time. Get notifications for status updates, deadlines, and interview schedules.',
    color: 'from-neon-pink to-neon-purple',
  },
  {
    icon: Trophy,
    title: 'Crack Interviews',
    description: 'Access interview prep resources, mock interviews, and company-specific tips. Walk in confident, walk out successful.',
    color: 'from-emerald-400 to-cyan-400',
  },
];

export const HowItWorksSection = () => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' });
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start end', 'end start'],
  });

  const lineHeight = useTransform(scrollYProgress, [0.1, 0.9], ['0%', '100%']);

  return (
    <section id="how-it-works" ref={sectionRef} className="py-32 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 section-gradient" />
      <div className="absolute top-1/3 right-0 w-96 h-96 bg-neon-purple/10 rounded-full blur-[150px]" />
      <div className="absolute bottom-1/3 left-0 w-80 h-80 bg-neon-blue/10 rounded-full blur-[120px]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <span className="text-primary text-sm font-semibold uppercase tracking-widest mb-4 block">
            How It Works
          </span>
          <h2 className="font-display text-4xl md:text-6xl font-bold text-foreground mb-6">
            From Profile to
            <span className="gradient-text"> Placement</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            A streamlined journey designed to get you from application to offer letter.
          </p>
        </motion.div>

        {/* Timeline */}
        <div className="max-w-4xl mx-auto relative">
          {/* Animated Line */}
          <div className="absolute left-1/2 md:left-8 -translate-x-1/2 md:translate-x-0 top-0 bottom-0 w-1 bg-border/30 rounded-full overflow-hidden">
            <motion.div
              style={{ height: lineHeight }}
              className="w-full timeline-line rounded-full"
            />
          </div>

          {/* Steps */}
          <div className="space-y-16 md:space-y-24">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isEven = index % 2 === 0;

              return (
                <motion.div
                  key={step.title}
                  initial={{ opacity: 0, x: isEven ? -50 : 50 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.8, delay: 0.2 + index * 0.15 }}
                  className={`relative flex items-center gap-8 ${
                    isEven ? 'md:flex-row' : 'md:flex-row-reverse'
                  } flex-col md:ml-0`}
                >
                  {/* Timeline Node */}
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={isInView ? { scale: 1 } : {}}
                    transition={{ 
                      duration: 0.5, 
                      delay: 0.4 + index * 0.15,
                      type: 'spring',
                      stiffness: 200,
                    }}
                    className="absolute left-1/2 md:left-8 -translate-x-1/2 md:translate-x-0 z-10"
                  >
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-2xl pulse-glow`}>
                      <Icon className="w-8 h-8 text-foreground" />
                    </div>
                    {/* Pulse ring */}
                    <motion.div
                      animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity, delay: index * 0.3 }}
                      className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${step.color} -z-10`}
                    />
                  </motion.div>

                  {/* Content Card */}
                  <div className={`w-full md:w-[calc(50%-60px)] ${isEven ? 'md:ml-auto md:pl-24' : 'md:mr-auto md:pr-24 md:ml-24'} pl-0 pt-20 md:pt-0`}>
                    <motion.div
                      whileHover={{ scale: 1.02, y: -5 }}
                      transition={{ duration: 0.3 }}
                      className="glass-card-glow p-8 relative group"
                    >
                      {/* Step number */}
                      <div className="absolute -top-3 -left-3 w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-sm font-bold text-primary-foreground shadow-lg">
                        {index + 1}
                      </div>

                      <h3 className="font-display text-2xl font-bold text-foreground mb-4 group-hover:text-primary transition-colors">
                        {step.title}
                      </h3>
                      <p className="text-muted-foreground leading-relaxed">
                        {step.description}
                      </p>

                      {/* Decorative arrow */}
                      <div 
                        className={`hidden md:block absolute top-1/2 -translate-y-1/2 w-8 h-8 ${
                          isEven ? '-left-4' : '-right-4'
                        }`}
                      >
                        <div className={`w-4 h-4 rotate-45 bg-card border-l border-t border-glass-border/30 ${
                          isEven ? '' : 'ml-4 border-l-0 border-r border-t-0 border-b'
                        }`} />
                      </div>

                      {/* Hover glow */}
                      <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-primary/10 rounded-full blur-[40px] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    </motion.div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};
