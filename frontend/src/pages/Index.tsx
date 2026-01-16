import { Navbar } from '@/components/Navbar';
import { HeroSection } from '@/components/HeroSection';
import { FeaturesSection } from '@/components/FeaturesSection';
import { DashboardPreview } from '@/components/DashboardPreview';
import { HowItWorksSection } from '@/components/HowItWorksSection';
import { TestimonialsSection } from '@/components/TestimonialsSection';
import { TrustSection } from '@/components/TrustSection';
import { Footer } from '@/components/Footer';
import { AIChatWidget } from '@/components/AIChatWidget';

const Index = () => {
  return (
    <main className="min-h-screen bg-background text-foreground overflow-x-hidden">
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <DashboardPreview />
      <HowItWorksSection />
      <TestimonialsSection />
      <TrustSection />
      <Footer />
      <AIChatWidget />
    </main>
  );
};

export default Index;
