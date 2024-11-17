// frontend/components/Chatbot.tsx
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { MessageSquare, X, Send } from 'lucide-react';

type Message = {
  id: number;
  text: string;
  isBot: boolean;
};

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Bonjour ! Je peux vous aider à analyser les amendements. Que souhaitez-vous savoir ?",
      isBot: true,
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      isBot: false,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Vérifier si l'input contient "merci"
    if (inputValue.toLowerCase().includes('merci')) {
      const botMessage = {
        id: messages.length + 2,
        text: 'De rien, c\'est avec plaisir',
        isBot: true,
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsLoading(false);
      return;
    }

    // Générer une réponse aléatoire avec des amendements fictifs
    const titresComplets = [
      'PLF POUR 2025',
      'PLF POUR 2026',
      'PLF POUR 2027',
      'PLF POUR 2028',
      'PLF POUR 2029',
      'PLF POUR 2030',
    ];
    const numeros = [860, 629, 921, 143, 672, 939];
    const reponse = `Voici la liste des amendements prévoyant une baisse des dépenses publiques :\n\n${numeros
      .sort(() => 0.5 - Math.random())
      .slice(0, 3)
      .map(
        (num, index) =>
          `- Amendement n° ${num} - ${titresComplets[index]} - 1ère lecture (1ère assemblée saisie) - n° ${Math.floor(
            Math.random() * 1000
          )}`
      )
      .join('\n')}`;

    setTimeout(() => {
      const botMessage = {
        id: messages.length + 2,
        text: reponse,
        isBot: true,
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsLoading(false);
    }, 4000);
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Bouton du chatbot */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white rounded-full p-4 shadow-lg transition-colors"
        >
          <MessageSquare className="w-6 h-6" />
        </button>
      )}

      {/* Fenêtre du chatbot */}
      {isOpen && (
        <div className="bg-white rounded-lg shadow-xl w-96 max-w-[calc(100vw-2rem)] h-[600px] max-h-[calc(100vh-2rem)] flex flex-col">
          {/* Header */}
          <div className="p-4 border-b flex justify-between items-center bg-blue-500 text-white rounded-t-lg">
            <h3 className="font-semibold">Assistant Agent</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-blue-600 rounded p-1"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.isBot ? 'justify-start' : 'justify-end'
                }`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    message.isBot
                      ? 'bg-gray-100 text-black'
                      : 'bg-blue-500 text-white'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 p-3 rounded-lg">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Posez votre question..."
                className="flex-1 p-2 border rounded-lg focus:outline-none focus:border-blue-500 text-gray-800"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}