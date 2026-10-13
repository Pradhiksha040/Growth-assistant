import { useState, useEffect } from 'react';
import type { Session, Message, Artifact, ProvidersResponse, TranscriptMetadata, HealthStatus } from './types';
import { api } from './services/api';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { ArtifactViewer } from './components/ArtifactViewer';
import { ProviderModal } from './components/ProviderModal';
import { Ship30Modal } from './components/Ship30Modal';
import { TranscriptsModal } from './components/TranscriptsModal';
import './App.css';

export function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [isArtifactViewerOpen, setIsArtifactViewerOpen] = useState(false);

  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [providersData, setProvidersData] = useState<ProvidersResponse | null>(null);
  const [transcripts, setTranscripts] = useState<TranscriptMetadata[]>([]);

  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [suggestedFollowups, setSuggestedFollowups] = useState<string[]>([]);

  // Modals
  const [isProviderModalOpen, setIsProviderModalOpen] = useState(false);
  const [isShip30ModalOpen, setIsShip30ModalOpen] = useState(false);
  const [isTranscriptsModalOpen, setIsTranscriptsModalOpen] = useState(false);

  // Load initial environment metadata
  useEffect(() => {
    let isMounted = true;
    Promise.all([
      api.getHealth().catch(() => null),
      api.listProviders().catch(() => null),
      api.listTranscripts().catch(() => []),
      api.listSessions().catch(() => [])
    ])
      .then(([healthData, provData, transData, sessData]) => {
        if (!isMounted) return;
        if (healthData) setHealth(healthData);
        if (provData) setProvidersData(provData);
        if (transData) setTranscripts(transData);
        if (sessData) {
          setSessions(sessData);
          if (sessData.length > 0) {
            setActiveSessionId((prev) => prev || sessData[0].id);
          }
        }
      })
      .catch((err) => {
        console.error('Initial load failed:', err);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Load messages & artifacts when activeSessionId changes
  useEffect(() => {
    if (!activeSessionId) return;

    let isMounted = true;
    Promise.all([
      api.getSessionMessages(activeSessionId).catch(() => []),
      api.listArtifacts(activeSessionId).catch(() => [])
    ]).then(([msgs, arts]) => {
      if (!isMounted) return;
      setMessages(msgs);
      setArtifacts(arts);
      if (arts.length > 0) {
        setActiveArtifact((prev) => prev || arts[0]);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [activeSessionId]);

  // Handler: Select Session
  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
    setSuggestedFollowups([]);
  };

  // Handler: Create New Chat
  const handleNewChat = async () => {
    try {
      const newSess = await api.createSession('New Conversation');
      setSessions((prev) => [newSess, ...prev]);
      setActiveSessionId(newSess.id);
      setMessages([]);
      setArtifacts([]);
      setActiveArtifact(null);
      setSuggestedFollowups([]);
      setIsArtifactViewerOpen(false);
    } catch (err) {
      console.error('Failed to create new chat:', err);
    }
  };

  // Handler: Delete Session
  const handleDeleteSession = async (id: string) => {
    try {
      await api.deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (activeSessionId === id) {
        const remaining = sessions.filter((s) => s.id !== id);
        if (remaining.length > 0) {
          setActiveSessionId(remaining[0].id);
        } else {
          setActiveSessionId(null);
          setMessages([]);
          setArtifacts([]);
        }
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  // Handler: Rename Session
  const handleRenameSession = async (id: string, newTitle: string) => {
    try {
      const updated = await api.updateSessionTitle(id, newTitle);
      setSessions((prev) =>
        prev.map((s) => (s.id === id ? { ...s, title: updated.title } : s))
      );
    } catch (err) {
      console.error('Failed to rename session:', err);
    }
  };

  // Handler: Send Message
  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    // Optimistic user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: activeSessionId || '',
      role: 'user',
      content: text,
      citations: [],
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const res = await api.sendMessage({
        sessionId: activeSessionId || undefined,
        message: text
      });

      // If backend created or returned a new session
      if (!activeSessionId || activeSessionId !== res.session_id) {
        setActiveSessionId(res.session_id);
        const updatedList = await api.listSessions().catch(() => []);
        setSessions(updatedList);
      }

      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUserMsg.id),
        { ...tempUserMsg, session_id: res.session_id },
        res.message
      ]);

      setSuggestedFollowups(res.suggested_followups || []);

      // Check if new artifacts were created
      const currentArts = await api.listArtifacts(res.session_id).catch(() => []);
      setArtifacts(currentArts);
      if (currentArts.length > 0) {
        setActiveArtifact(currentArts[0]);
        // Open artifact viewer if artifact was created
        setIsArtifactViewerOpen(true);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        session_id: activeSessionId || '',
        role: 'assistant',
        content: `⚠️ **Error communicating with backend:** ${
          err instanceof Error ? err.message : String(err)
        }`,
        citations: [],
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handler: Regenerate Response
  const handleRegenerate = (_msg: Message) => {
    const userMsgs = messages.filter((m) => m.role === 'user');
    if (userMsgs.length > 0) {
      const lastUser = userMsgs[userMsgs.length - 1];
      handleSendMessage(lastUser.content);
    }
  };

  // Handler: Ship 30 Essay Generated
  const handleEssayGenerated = (artifact: Artifact) => {
    setArtifacts((prev) => [artifact, ...prev]);
    setActiveArtifact(artifact);
    setIsArtifactViewerOpen(true);
  };

  const activeSessionObj = sessions.find((s) => s.id === activeSessionId);
  const currentProvider =
    providersData?.providers.find((p) => p.name === providersData.active_provider) ||
    null;

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onRenameSession={handleRenameSession}
        health={health}
        activeProvider={currentProvider}
        onOpenTranscripts={() => setIsTranscriptsModalOpen(true)}
        onOpenProviders={() => setIsProviderModalOpen(true)}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Main View Area: Chat + Artifact Viewer */}
      <main className="main-content">
        <ChatArea
          sessionTitle={activeSessionObj?.title || 'New Conversation'}
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          onRegenerate={handleRegenerate}
          suggestedFollowups={suggestedFollowups}
          onOpenShip30={() => setIsShip30ModalOpen(true)}
          onOpenProviders={() => setIsProviderModalOpen(true)}
          activeProvider={currentProvider}
          onOpenSidebar={() => setIsSidebarOpen(true)}
          artifacts={artifacts}
          onSelectArtifact={(art) => {
            setActiveArtifact(art);
            setIsArtifactViewerOpen(true);
          }}
          isArtifactViewerOpen={isArtifactViewerOpen}
          onToggleArtifactViewer={() =>
            setIsArtifactViewerOpen((prev) => !prev)
          }
        />

        {/* Artifact Viewer (Claude Artifacts style split pane) */}
        {isArtifactViewerOpen && activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setIsArtifactViewerOpen(false)}
            isOpen={isArtifactViewerOpen}
          />
        )}
      </main>

      {/* Modals */}
      <ProviderModal
        isOpen={isProviderModalOpen}
        onClose={() => setIsProviderModalOpen(false)}
        providersData={providersData}
        onProviderChanged={async () => {
          const updated = await api.listProviders().catch(() => null);
          if (updated) setProvidersData(updated);
        }}
      />

      <Ship30Modal
        isOpen={isShip30ModalOpen}
        onClose={() => setIsShip30ModalOpen(false)}
        sessionId={activeSessionId}
        onEssayGenerated={handleEssayGenerated}
      />

      <TranscriptsModal
        isOpen={isTranscriptsModalOpen}
        onClose={() => setIsTranscriptsModalOpen(false)}
        transcripts={transcripts}
        onRefresh={async () => {
          const updated = await api.listTranscripts().catch(() => []);
          setTranscripts(updated);
        }}
      />
    </div>
  );
}

export default App;
