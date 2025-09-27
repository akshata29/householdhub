"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  MessageCircle, 
  X, 
  Send, 
  Bot,
  User,
  Loader2,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Maximize2,
  Minimize2,
  Sparkles
} from "lucide-react";

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  isStreaming?: boolean;
}

interface Citation {
  source: string;
  description: string;
  confidence?: number;
}

interface QueryRequest {
  query: string;
  household_id?: string;
  account_id?: string;
  user_context?: Record<string, any>;
}

interface QueryResponse {
  answer: string;
  citations: Citation[];
  sql_generated?: string;
  execution_time_ms: number;
  agent_calls: string[];
}

interface CopilotPanelProps {
  householdId?: string;
}

const ORCHESTRATOR_BASE_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:8003';

const quickActions = [
  { 
    id: 'top-cash', 
    icon: '💰', 
    label: 'Top Cash Balances', 
    query: 'What are the top cash balances by household?',
    description: 'View highest cash positions across accounts'
  },
  { 
    id: 'crm-insights', 
    icon: '📝', 
    label: 'Recent CRM Notes', 
    query: 'What are the recent points of interest from CRM notes?',
    description: 'Get insights from latest client interactions'
  },
  { 
    id: 'allocation-drift', 
    icon: '⚖️', 
    label: 'Allocation Analysis', 
    query: 'Show me any allocation mismatches that need rebalancing',
    description: 'Check portfolio drift vs target allocation'
  },
  { 
    id: 'rmd-status', 
    icon: '📅', 
    label: 'RMD Status', 
    query: 'What are the upcoming RMD deadlines and current status?',
    description: 'Review required minimum distributions'
  },
  { 
    id: 'performance-summary', 
    icon: '📊', 
    label: 'Performance Summary', 
    query: 'Give me a performance summary for this quarter',
    description: 'Analyze portfolio returns and benchmarks'
  },
  { 
    id: 'executive-summary', 
    icon: '📋', 
    label: 'Executive Summary', 
    query: 'Provide an executive summary of the household',
    description: 'Comprehensive household overview'
  }
];

export function CopilotPanel({ householdId }: CopilotPanelProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const [isMaximized, setIsMaximized] = React.useState(false);
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: householdId 
        ? `Hello! I'm your WealthOps AI assistant. I can help you analyze portfolios, review cash positions, check CRM insights, and answer questions about this household. What would you like to explore today?`
        : `Hello! I'm your WealthOps AI assistant. I can help you with general wealth management questions, portfolio analysis, and provide insights about household management. Feel free to ask me anything!`,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [showQuickActions, setShowQuickActions] = React.useState(true);

  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  React.useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const sendQuery = async (query: string) => {
    if (!query.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setShowQuickActions(false);

    // Create streaming message
    const streamingMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
      citations: []
    };

    setMessages(prev => [...prev, streamingMessage]);

    try {
      const request: QueryRequest = {
        query,
        household_id: householdId || 'general',
        user_context: {
          timestamp: new Date().toISOString(),
          session_id: `session_${Date.now()}`
        }
      };

      // Try streaming first, fall back to sync if streaming fails
      let response: QueryResponse | null = null;
      
      try {
        const streamResponse = await fetch(`${ORCHESTRATOR_BASE_URL}/copilot/query/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request)
        });

        if (streamResponse.ok && streamResponse.body) {
          const reader = streamResponse.body.getReader();
          const decoder = new TextDecoder();
          let accumulatedContent = '';

          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value);
              const lines = chunk.split('\n');

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const data = JSON.parse(line.slice(6));
                    
                    if (data.type === 'status') {
                      // Update streaming message with status
                      setMessages(prev => prev.map(msg => 
                        msg.id === streamingMessage.id 
                          ? { ...msg, content: `${data.content}...` }
                          : msg
                      ));
                    } else if (data.type === 'complete') {
                      // Parse final response
                      response = JSON.parse(data.content);
                      break;
                    }
                  } catch (e) {
                    console.warn('Failed to parse SSE data:', line);
                  }
                }
              }
            }
          } finally {
            reader.releaseLock();
          }
        }
      } catch (streamError) {
        console.warn('Streaming failed, falling back to sync:', streamError);
      }

      // Fallback to sync API if streaming didn't work
      if (!response) {
        const syncResponse = await fetch(`${ORCHESTRATOR_BASE_URL}/copilot/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request)
        });

        if (!syncResponse.ok) {
          throw new Error(`API Error: ${syncResponse.status} ${syncResponse.statusText}`);
        }

        response = await syncResponse.json();
      }

      // Update the streaming message with final content
      setMessages(prev => prev.map(msg => 
        msg.id === streamingMessage.id 
          ? {
              ...msg,
              content: response!.answer,
              citations: response!.citations,
              isStreaming: false
            }
          : msg
      ));

    } catch (error) {
      console.error('Query failed:', error);
      
      // Update with error message
      setMessages(prev => prev.map(msg => 
        msg.id === streamingMessage.id 
          ? {
              ...msg,
              content: `I apologize, but I encountered an error while processing your request. This might be because the backend services are not running. Please ensure the orchestrator is available at ${ORCHESTRATOR_BASE_URL}. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
              isStreaming: false,
              citations: []
            }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: typeof quickActions[0]) => {
    sendQuery(action.query);
  };

  const handleSendMessage = () => {
    sendQuery(inputValue);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    // Could add a toast notification here
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const panelSize = isMaximized 
    ? { width: '800px', height: '600px', bottom: '24px', right: '24px' }
    : { width: '400px', height: '500px', bottom: '24px', left: '24px' };

  if (!isOpen) {
    return (
      <div className="copilot-trigger">
        <Button
          onClick={() => setIsOpen(true)}
          className="copilot-button"
          size="lg"
        >
          <MessageCircle className="copilot-icon" />
          <span className="copilot-text">AI Assistant</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="copilot-panel" style={panelSize}>
      {/* Header */}
      <div className="copilot-header">
        <div className="header-info">
          <div className="header-title">
            <Bot className="header-icon" />
            <span>WealthOps AI Assistant</span>
            <Badge variant="secondary" className="status-badge">
              Online
            </Badge>
          </div>
          <p className="header-subtitle">
            Ask me about portfolios, cash positions, CRM insights, and more
          </p>
        </div>
        <div className="header-actions">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsMaximized(!isMaximized)}
            className="action-btn"
          >
            {isMaximized ? <Minimize2 className="action-icon" /> : <Maximize2 className="action-icon" />}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(false)}
            className="action-btn"
          >
            <X className="action-icon" />
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      {showQuickActions && messages.length <= 1 && (
        <div className="quick-actions">
          <div className="quick-actions-header">
            <Sparkles className="quick-actions-icon" />
            <span>Quick Actions</span>
          </div>
          <div className="quick-actions-grid">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action)}
                className="quick-action-card"
                disabled={isLoading}
              >
                <div className="action-icon-wrapper">
                  <span className="action-emoji">{action.icon}</span>
                </div>
                <div className="action-content">
                  <div className="action-label">{action.label}</div>
                  <div className="action-description">{action.description}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message-wrapper ${message.type}`}>
            <div className="message-content">
              {message.type === 'assistant' && (
                <div className="message-avatar assistant">
                  <Bot className="avatar-icon" />
                </div>
              )}
              {message.type === 'user' && (
                <div className="message-avatar user">
                  <User className="avatar-icon" />
                </div>
              )}
              
              <div className="message-body">
                <div className="message-text">
                  {message.isStreaming && !message.content && (
                    <div className="streaming-indicator">
                      <Loader2 className="loading-spinner" />
                      <span>Thinking...</span>
                    </div>
                  )}
                  {message.content}
                  {message.isStreaming && message.content && (
                    <span className="cursor-blink">|</span>
                  )}
                </div>
                
                {message.citations && message.citations.length > 0 && (
                  <div className="citations">
                    <div className="citations-header">Sources:</div>
                    {message.citations.map((citation, index) => (
                      <div key={index} className="citation-item">
                        <span className="citation-source">{citation.source}</span>
                        <span className="citation-description">{citation.description}</span>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="message-meta">
                  <span className="message-time">{formatTimestamp(message.timestamp)}</span>
                  {message.type === 'assistant' && !message.isStreaming && (
                    <div className="message-actions">
                      <button
                        onClick={() => copyMessage(message.content)}
                        className="message-action"
                        title="Copy message"
                      >
                        <Copy className="action-icon-small" />
                      </button>
                      <button className="message-action" title="Helpful">
                        <ThumbsUp className="action-icon-small" />
                      </button>
                      <button className="message-action" title="Not helpful">
                        <ThumbsDown className="action-icon-small" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="input-container">
        <div className="input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about the portfolio..."
            className="message-input"
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="send-button"
            size="sm"
          >
            {isLoading ? (
              <Loader2 className="loading-icon" />
            ) : (
              <Send className="send-icon" />
            )}
          </Button>
        </div>
        <div className="input-hint">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
}