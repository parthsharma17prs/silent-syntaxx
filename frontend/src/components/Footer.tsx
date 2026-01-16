import { motion } from 'framer-motion';
import { Twitter, Linkedin, Instagram, Github, Mail, MapPin, Phone } from 'lucide-react';

const PORTAL_BASE = (import.meta as any).env?.VITE_PORTAL_BASE || '/portal';

const footerLinks = {
  Product: ['Features', 'Dashboard', 'Pricing', 'Changelog'],
  Company: ['About Us', 'Careers', 'Blog', 'Press'],
  Resources: ['Help Center', 'Community', 'Tutorials', 'API Docs'],
  Legal: ['Privacy Policy', 'Terms of Service', 'Cookie Policy'],
};

const socialLinks = [
  { icon: Twitter, href: '#', label: 'Twitter' },
  { icon: Linkedin, href: '#', label: 'LinkedIn' },
  { icon: Instagram, href: '#', label: 'Instagram' },
  { icon: Github, href: '#', label: 'GitHub' },
];

export const Footer = () => {
  return (
    <footer className="relative pt-24 pb-8 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-t from-background via-card/20 to-transparent" />
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-neon-purple/5 rounded-full blur-[150px]" />
      <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-neon-blue/5 rounded-full blur-[120px]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <h2 className="font-display text-4xl md:text-5xl font-bold text-foreground mb-6">
            Ready to Command
            <span className="gradient-text"> Your Career?</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto mb-8">
            Join 50,000+ students already using Silent Syntax to land their dream roles.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-4 rounded-xl bg-gradient-to-r from-neon-purple to-neon-blue text-foreground font-semibold text-lg shadow-xl hover:shadow-2xl hover:shadow-neon-purple/20 transition-all"
            onClick={() => window.location.assign(`${PORTAL_BASE}/register.html`)}
          >
            Get Started Free
          </motion.button>
        </motion.div>

        {/* Main Footer */}
        <div className="grid md:grid-cols-2 lg:grid-cols-6 gap-12 pb-12 border-b border-border/30">
          {/* Brand */}
          <div className="lg:col-span-2">
            <a href="#" className="flex items-center gap-2 mb-6">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-purple to-neon-blue flex items-center justify-center">
                <img
                  src="/brand/silent-syntax-icon.png"
                  alt="Silent Syntax"
                  className="w-6 h-6"
                  draggable={false}
                />
              </div>
              <span className="font-display text-2xl font-semibold text-foreground">Silent Syntax</span>
            </a>
            <p className="text-muted-foreground mb-6 max-w-xs">
              The ultimate career command center for students. Track, apply, and succeed.
            </p>
            
            {/* Contact Info */}
            <div className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-primary" />
                <span>hello@silentsyntax.com</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-primary" />
                <span>+91 98765 43210</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-primary" />
                <span>Bangalore, India</span>
              </div>
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="font-semibold text-foreground mb-4">{category}</h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-muted-foreground hover:text-foreground transition-colors text-sm"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8">
          <p className="text-sm text-muted-foreground">
            © 2026 Silent Syntax. All rights reserved.
          </p>
          
          {/* Social Links */}
          <div className="flex items-center gap-4">
            {socialLinks.map((social) => {
              const Icon = social.icon;
              return (
                <motion.a
                  key={social.label}
                  href={social.href}
                  whileHover={{ scale: 1.1, y: -2 }}
                  className="w-10 h-10 rounded-lg glass-card flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-primary/20 transition-all"
                  aria-label={social.label}
                >
                  <Icon className="w-5 h-5" />
                </motion.a>
              );
            })}
          </div>
        </div>
      </div>
    </footer>
  );
};
