import { useRef, useEffect, useState } from 'react';
import { motion, useInView } from 'framer-motion';
import { Quote, ChevronLeft, ChevronRight } from 'lucide-react';

const testimonials = [
  {
    name: 'Priya Sharma',
    role: 'Software Engineer',
    company: 'Google',
    quote: 'Silent Syntax transformed my placement journey. The AI resume analyzer helped me land interviews at top tech companies!',
    image: 'PS',
  },
  {
    name: 'Rahul Verma',
    role: 'Data Scientist',
    company: 'Microsoft',
    quote: 'The real-time tracking feature is incredible. I never missed a deadline or interview. Highly recommend!',
    image: 'RV',
  },
  {
    name: 'Ananya Patel',
    role: 'Product Manager',
    company: 'Amazon',
    quote: 'From building my profile to cracking interviews, Silent Syntax was my go-to platform. The verified companies feature gave me peace of mind.',
    image: 'AP',
  },
  {
    name: 'Vikram Singh',
    role: 'Frontend Developer',
    company: 'Meta',
    quote: 'The placement readiness score motivated me to improve constantly. Ended up with 3 offers from dream companies!',
    image: 'VS',
  },
  {
    name: 'Sneha Reddy',
    role: 'ML Engineer',
    company: 'Apple',
    quote: 'What I love most is how everything is in one place. No more juggling between spreadsheets and emails.',
    image: 'SR',
  },
];

export const TestimonialsSection = () => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(sectionRef, { once: true, margin: '-100px' });
  const [activeIndex, setActiveIndex] = useState(2);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  useEffect(() => {
    if (!isAutoPlaying) return;
    
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % testimonials.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [isAutoPlaying]);

  const handlePrev = () => {
    setIsAutoPlaying(false);
    setActiveIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  const handleNext = () => {
    setIsAutoPlaying(false);
    setActiveIndex((prev) => (prev + 1) % testimonials.length);
  };

  return (
    <section id="reviews" ref={sectionRef} className="py-32 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-card/30 to-transparent" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-neon-purple/5 rounded-full blur-[150px]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <span className="text-primary text-sm font-semibold uppercase tracking-widest mb-4 block">
            Testimonials
          </span>
          <h2 className="font-display text-4xl md:text-6xl font-bold text-foreground mb-6">
            Loved by
            <span className="gradient-text"> Students</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Join thousands of students who have transformed their career journey with Silent Syntax.
          </p>
        </motion.div>

        {/* Carousel */}
        <div className="relative max-w-5xl mx-auto">
          {/* Navigation Buttons */}
          <button
            onClick={handlePrev}
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 md:-translate-x-12 z-20 w-12 h-12 rounded-full glass-card flex items-center justify-center text-foreground hover:bg-primary/20 transition-colors"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <button
            onClick={handleNext}
            className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 md:translate-x-12 z-20 w-12 h-12 rounded-full glass-card flex items-center justify-center text-foreground hover:bg-primary/20 transition-colors"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          {/* Cards Container */}
          <div className="relative h-[400px] flex items-center justify-center">
            {testimonials.map((testimonial, index) => {
              const offset = index - activeIndex;
              const absOffset = Math.abs(offset);
              const isActive = index === activeIndex;

              // Calculate circular position
              let adjustedOffset = offset;
              if (offset > testimonials.length / 2) adjustedOffset = offset - testimonials.length;
              if (offset < -testimonials.length / 2) adjustedOffset = offset + testimonials.length;

              const absAdjustedOffset = Math.abs(adjustedOffset);

              return (
                <motion.div
                  key={testimonial.name}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{
                    opacity: absAdjustedOffset > 2 ? 0 : 1 - absAdjustedOffset * 0.3,
                    scale: 1 - absAdjustedOffset * 0.15,
                    x: adjustedOffset * 280,
                    zIndex: 10 - absAdjustedOffset,
                    filter: isActive ? 'blur(0px)' : `blur(${absAdjustedOffset * 2}px)`,
                  }}
                  transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                  className="absolute w-full max-w-md cursor-pointer"
                  onClick={() => {
                    setIsAutoPlaying(false);
                    setActiveIndex(index);
                  }}
                >
                  <div className={`glass-card-glow p-8 ${isActive ? 'neon-border' : ''}`}>
                    <Quote className="w-10 h-10 text-primary/30 mb-4" />
                    
                    <p className="text-foreground text-lg leading-relaxed mb-6">
                      "{testimonial.quote}"
                    </p>

                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-neon-purple to-neon-blue flex items-center justify-center font-bold text-foreground">
                        {testimonial.image}
                      </div>
                      <div>
                        <div className="font-semibold text-foreground">{testimonial.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {testimonial.role} at {testimonial.company}
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Dots */}
          <div className="flex justify-center gap-2 mt-8">
            {testimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => {
                  setIsAutoPlaying(false);
                  setActiveIndex(index);
                }}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  index === activeIndex
                    ? 'w-8 bg-primary'
                    : 'bg-muted-foreground/30 hover:bg-muted-foreground/50'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
