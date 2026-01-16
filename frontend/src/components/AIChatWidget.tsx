import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Bot, User } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Message {
  id: number;
  text: string;
  isBot: boolean;
}

const initialMessages: Message[] = [
  {
    id: 1,
    text: "Hi! I'm your Silent Syntax AI assistant. How can I help you today with your placement journey?",
    isBot: true,
  },
];

const quickReplies = [
  'How do I improve my resume?',
  'Upcoming interview tips',
  'Track my applications',
  'Find internships',
];

export const AIChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = (text: string) => {
    if (!text.trim()) return;

    const newUserMessage: Message = {
      id: messages.length + 1,
      text: text.trim(),
      isBot: false,
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const botResponses: Record<string, string> = {
        'How do I improve my resume?': "Great question! Here are my top tips:\n\n1. Use action verbs and quantify achievements\n2. Tailor your resume for each role\n3. Include relevant keywords from job descriptions\n4. Keep it clean and well-formatted\n\nWould you like me to analyze your resume?",
        'Upcoming interview tips': "Here are key tips for your interviews:\n\n1. Research the company thoroughly\n2. Practice STAR method for behavioral questions\n3. Prepare 3-5 questions to ask\n4. Test your tech setup for virtual interviews\n\nGood luck! 🎯",
        'Track my applications': "You currently have:\n• 24 applications submitted\n• 8 shortlisted\n• 3 interviews scheduled\n• 2 offers pending\n\nYour next interview is on Monday at 2 PM. Would you like tips for it?",
        'Find internships': "Based on your profile, here are top matches:\n\n1. Google - SWE Intern (95% match)\n2. Microsoft - PM Intern (92% match)\n3. Amazon - Data Intern (88% match)\n\nShall I help you apply to any of these?",
      };

      const response = botResponses[text] || 
        "Thanks for your message! I can help you with resume tips, interview prep, application tracking, and finding opportunities. What would you like to explore?";

      const newBotMessage: Message = {
        id: messages.length + 2,
        text: response,
        isBot: true,
      };

      setMessages((prev) => [...prev, newBotMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <>
      {/* Chat Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 1, type: 'spring', stiffness: 200 }}
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 z-50 w-16 h-16 rounded-2xl bg-gradient-to-r from-neon-purple to-neon-blue flex items-center justify-center shadow-2xl hover:shadow-neon-purple/30 transition-all ${
          isOpen ? 'scale-0' : 'scale-100'
        }`}
      >
        <Bot className="w-8 h-8 text-foreground" />
        <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-green-500 border-2 border-background animate-pulse" />
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="fixed bottom-6 right-6 z-50 w-[380px] h-[550px] glass-card-glow flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border/50 bg-gradient-to-r from-neon-purple/10 to-neon-blue/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-purple to-neon-blue flex items-center justify-center">
                  <Bot className="w-5 h-5 text-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Silent Syntax AI</h3>
                  <span className="text-xs text-green-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                    Online
                  </span>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 rounded-lg hover:bg-muted flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-3 ${message.isBot ? '' : 'flex-row-reverse'}`}
                >
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      message.isBot
                        ? 'bg-gradient-to-br from-neon-purple to-neon-blue'
                        : 'bg-primary'
                    }`}
                  >
                    {message.isBot ? (
                      <Bot className="w-4 h-4 text-foreground" />
                    ) : (
                      <User className="w-4 h-4 text-primary-foreground" />
                    )}
                  </div>
                  <div
                    className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm whitespace-pre-line ${
                      message.isBot
                        ? 'bg-muted text-foreground rounded-tl-none'
                        : 'bg-primary text-primary-foreground rounded-tr-none'
                    }`}
                  >
                    {message.text}
                  </div>
                </motion.div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-3"
                >
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-purple to-neon-blue flex items-center justify-center">
                    <Bot className="w-4 h-4 text-foreground" />
                  </div>
                  <div className="bg-muted rounded-2xl rounded-tl-none px-4 py-3 flex gap-1">
                    <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Replies */}
            {messages.length <= 2 && (
              <div className="px-4 pb-2 flex flex-wrap gap-2">
                {quickReplies.map((reply) => (
                  <button
                    key={reply}
                    onClick={() => handleSend(reply)}
                    className="px-3 py-1.5 rounded-full text-xs border border-primary/30 text-primary hover:bg-primary/10 transition-colors"
                  >
                    {reply}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-border/50">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend(inputValue)}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-3 rounded-xl bg-muted border border-border/50 text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 text-sm"
                />
                <Button
                  onClick={() => handleSend(inputValue)}
                  disabled={!inputValue.trim()}
                  variant="hero"
                  size="icon"
                  className="w-12 h-12 rounded-xl"
                >
                  <Send className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
