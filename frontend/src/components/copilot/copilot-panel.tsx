"use client";

import * as React from "react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DataSourceBadge } from "@/components/data-source-indicator";
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
  Sparkles,
  RotateCcw,
  Database,
  ChevronDown,
  ChevronUp,
  DollarSign,
  FileText,
  BarChart3,
  Calendar,
  TrendingUp,
  ClipboardList,
  Server,
  Zap,
  CheckCircle,
  XCircle,
  AlertCircle
} from "lucide-react";

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  isStreaming?: boolean;
  sqlQuery?: string;
  executionTime?: number;
  agentCalls?: string[];
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

interface ServiceStatus {
  orchestrator: boolean;
  nl2sql: boolean;
}

const ORCHESTRATOR_BASE_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:9000';
const NL2SQL_BASE_URL = process.env.NEXT_PUBLIC_NL2SQL_URL || 'http://localhost:9001';

// Service Status Indicator Component (Orchestrator & NL2SQL only - Database uses DataSourceBadge)
function ServiceStatusIndicator({ 
  status,
  onRefresh 
}: { 
  status: ServiceStatus;
  onRefresh: () => void;
}) {
  const getStatusIcon = (isConnected: boolean) => {
    if (isConnected) {
      return <CheckCircle className="w-3 h-3 text-green-500" />;
    } else {
      return <XCircle className="w-3 h-3 text-red-500" />;
    }
  };

  const getOverallStatus = () => {
    const connectedCount = Object.values(status).filter(Boolean).length;
    const totalServices = Object.keys(status).length;
    
    if (connectedCount === totalServices) {
      return { text: "All Systems Online", icon: CheckCircle };
    } else if (connectedCount > 0) {
      return { text: "Partial Connection", icon: AlertCircle };
    } else {
      return { text: "Systems Offline", icon: XCircle };
    }
  };

  const overall = getOverallStatus();

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1">
        <overall.icon className="w-3 h-3 text-white" />
        <span className="text-xs text-white/90 font-medium">{overall.text}</span>
      </div>
      
      <div className="flex items-center gap-1 text-xs">
        <div className="flex items-center gap-1 bg-white/10 px-1.5 py-0.5 rounded" title="Orchestrator Service (Port 9000)">
          <Server className="w-2.5 h-2.5 text-white/80" />
          {status.orchestrator ? (
            <CheckCircle className="w-3 h-3 text-green-400" />
          ) : (
            <XCircle className="w-3 h-3 text-red-400" />
          )}
        </div>
        
        <div className="flex items-center gap-1 bg-white/10 px-1.5 py-0.5 rounded" title="NL2SQL Agent (Port 9001)">
          <Zap className="w-2.5 h-2.5 text-white/80" />
          {status.nl2sql ? (
            <CheckCircle className="w-3 h-3 text-green-400" />
          ) : (
            <XCircle className="w-3 h-3 text-red-400" />
          )}
        </div>
        
        {/* Database status is handled by DataSourceBadge in header */}
        
        <button 
          onClick={onRefresh}
          className="ml-1 p-1 hover:bg-white/20 rounded transition-colors"
          title="Refresh status"
        >
          <RotateCcw className="w-3 h-3 text-white/80 hover:text-white" />
        </button>
      </div>
    </div>
  );
}

// SQL Query Display Component
function SQLQueryDisplay({ 
  query, 
  executionTime, 
  agentCalls 
}: { 
  query: string; 
  executionTime?: number; 
  agentCalls?: string[] 
}) {
  const [isExpanded, setIsExpanded] = React.useState(false);

  return (
    <div className="sql-query-section mt-3 border border-gray-200 dark:border-gray-700 rounded-lg">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full p-3 text-sm font-medium text-left hover:bg-gray-50 dark:hover:bg-gray-800 rounded-t-lg"
      >
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-blue-600" />
          <span>SQL Query Details</span>
          {executionTime && (
            <Badge variant="secondary" className="text-xs">
              {executionTime}ms
            </Badge>
          )}
          {agentCalls && agentCalls.length > 0 && (
            <Badge variant="outline" className="text-xs">
              {agentCalls.join(', ')}
            </Badge>
          )}
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      
      {isExpanded && (
        <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <pre className="text-sm bg-gray-900 text-green-400 p-3 rounded overflow-x-auto">
            <code>{query}</code>
          </pre>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>Generated SQL query used to fetch the data</span>
            <button
              onClick={() => navigator.clipboard.writeText(query)}
              className="flex items-center gap-1 hover:text-gray-700 dark:hover:text-gray-300"
            >
              <Copy className="w-3 h-3" />
              Copy
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Quick actions function that provides context-aware queries
const getQuickActions = (householdId?: string) => [
  { 
    id: 'top-cash', 
    icon: DollarSign, 
    label: 'Cash Analysis', 
    query: householdId 
      ? 'What is the cash position for this household?'
      : 'What are the top cash balances by household?',
    description: householdId 
      ? 'View this household\'s cash positions'
      : 'View highest cash positions across all households'
  },
  { 
    id: 'crm-insights', 
    icon: FileText, 
    label: 'Recent CRM Notes', 
    query: householdId
      ? 'What are the recent CRM notes and interactions for this household?'
      : 'What are the recent points of interest from CRM notes?',
    description: householdId
      ? 'Get insights from this household\'s interactions'
      : 'Get insights from all interactions'
  },
  { 
    id: 'allocation-drift', 
    icon: BarChart3, 
    label: 'Allocation Analysis', 
    query: householdId
      ? 'Show me the allocation breakdown and any rebalancing needs for this household'
      : 'Show me any allocation mismatches that need rebalancing',
    description: householdId
      ? 'Check this household\'s portfolio drift'
      : 'Check portfolio drift across households'
  },
  { 
    id: 'rmd-status', 
    icon: Calendar, 
    label: 'RMD Status', 
    query: householdId
      ? 'What are the RMD requirements and status for this household?'
      : 'What are the upcoming RMD deadlines and current status?',
    description: householdId
      ? 'Review this household\'s distributions'
      : 'Review all RMD distributions'
  },
  { 
    id: 'performance-summary', 
    icon: TrendingUp, 
    label: 'Performance', 
    query: householdId
      ? 'Give me a performance summary for this household for this quarter'
      : 'Give me a performance summary for this quarter',
    description: householdId
      ? 'Analyze this household\'s returns'
      : 'Analyze returns across households'
  },
  { 
    id: 'executive-summary', 
    icon: ClipboardList, 
    label: 'Executive Summary', 
    query: householdId
      ? 'Provide an executive summary for this household'
      : 'Provide an executive summary of all households',
    description: householdId
      ? 'Comprehensive overview of this household'
      : 'Comprehensive overview of all households'
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
        ? `Hello! I can help you analyze this specific household's portfolios, cash positions, performance, and CRM insights. All my responses will be focused on this household's data only. What would you like to explore?`
        : `Hello! I can help with wealth management questions across all households - portfolio analysis, cash positions, performance comparisons, and insights. What would you like to know?`,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [showQuickActions, setShowQuickActions] = React.useState(true);
  const [serviceStatus, setServiceStatus] = React.useState<ServiceStatus>({
    orchestrator: false,
    nl2sql: false
  });

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

  React.useEffect(() => {
    if (isOpen) {
      // Check service health when panel opens
      checkAllServices();
      
      // Set up periodic health checks every 30 seconds
      const interval = setInterval(checkAllServices, 30000);
      
      return () => clearInterval(interval);
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
              sqlQuery: response!.sql_generated,
              executionTime: response!.execution_time_ms,
              agentCalls: response!.agent_calls,
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

  const quickActions = getQuickActions(householdId);

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

  const refreshChat = () => {
    setMessages([
      {
        id: '1',
        type: 'assistant',
        content: householdId 
          ? `Hello! I can help you analyze portfolios, cash positions, and CRM insights for this household. What would you like to explore?`
          : `Hello! I can help with wealth management questions, portfolio analysis, and household insights. What would you like to know?`,
        timestamp: new Date()
      }
    ]);
    setShowQuickActions(true);
    setInputValue('');
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Health check functions
  const checkOrchestratorHealth = async (): Promise<boolean> => {
    try {
      const response = await fetch(`${ORCHESTRATOR_BASE_URL}/health`, { 
        method: 'GET',
        timeout: 3000
      } as any);
      return response.ok;
    } catch (error) {
      return false;
    }
  };

  const checkNL2SQLHealth = async (): Promise<boolean> => {
    try {
      const response = await fetch(`${NL2SQL_BASE_URL}/health`, { 
        method: 'GET',
        timeout: 3000
      } as any);
      return response.ok;
    } catch (error) {
      return false;
    }
  };

  // Database health is managed by the existing DataSourceIndicator system

  const checkAllServices = async () => {
    const [orchestratorOk, nl2sqlOk] = await Promise.all([
      checkOrchestratorHealth(),
      checkNL2SQLHealth()
    ]);

    setServiceStatus({
      orchestrator: orchestratorOk,
      nl2sql: nl2sqlOk
    });
  };

  const panelSize = isMaximized 
    ? { width: '900px', height: '700px', bottom: '24px', right: '24px' }
    : { width: '420px', height: '600px', bottom: '24px', right: '24px' };

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
    <div className="copilot-panel flex flex-col bg-white dark:bg-gray-900 rounded-xl overflow-hidden" style={panelSize}>
      {/* Header */}
      <div className="copilot-header">
        <div className="header-info">
          <div className="header-title">
            <Bot className="w-5 h-5" />
            <span className="font-semibold">WealthOps AI</span>
          </div>
          <div className="mt-1 flex items-center gap-2">
            <DataSourceBadge className="text-xs" />
            <ServiceStatusIndicator 
              status={serviceStatus} 
              onRefresh={checkAllServices}
            />
          </div>
          <p className="text-xs text-gray-300 mt-1 opacity-90">
            Ask about portfolios, cash positions, CRM insights
          </p>
        </div>
        <div className="header-actions">
          <Button
            variant="ghost"
            size="sm"
            onClick={refreshChat}
            className="action-btn"
            title="Refresh chat"
          >
            <RotateCcw className="action-icon" />
          </Button>
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
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Quick Actions</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action)}
                className="flex items-center gap-2 p-2 text-left bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-lg transition-colors text-sm disabled:opacity-50"
                disabled={isLoading}
              >
                <action.icon className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <div className="min-w-0 flex-1">
                  <div className="font-medium text-gray-900 dark:text-gray-100 truncate">{action.label}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{action.description}</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="messages-container flex-1 overflow-y-auto p-4">
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
                  {message.content && message.type === 'assistant' ? (
                    <div className="prose prose-sm max-w-none dark:prose-invert">
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          // Customize code blocks
                          code: ({className, children, ...props}: any) => {
                            const isInline = !className?.includes('language-');
                            return isInline ? (
                              <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm" {...props}>
                                {children}
                              </code>
                            ) : (
                              <pre className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto">
                                <code {...props}>{children}</code>
                              </pre>
                            );
                          },
                          // Customize tables
                          table: ({children, ...props}) => (
                            <div className="overflow-x-auto">
                              <table className="min-w-full border border-gray-300 dark:border-gray-600" {...props}>
                                {children}
                              </table>
                            </div>
                          ),
                          th: ({children, ...props}) => (
                            <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 bg-gray-50 dark:bg-gray-700 font-semibold" {...props}>
                              {children}
                            </th>
                          ),
                          td: ({children, ...props}) => (
                            <td className="border border-gray-300 dark:border-gray-600 px-4 py-2" {...props}>
                              {children}
                            </td>
                          ),
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    message.content
                  )}
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

                {/* SQL Query Display */}
                {message.sqlQuery && message.type === 'assistant' && (
                  <SQLQueryDisplay 
                    query={message.sqlQuery} 
                    executionTime={message.executionTime}
                    agentCalls={message.agentCalls}
                  />
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
      <div className="border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about the portfolio..."
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="px-3 py-2"
            size="sm"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
}