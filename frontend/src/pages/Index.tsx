import { useEffect, useRef, useState } from 'react';
import { ReactFlowProvider } from 'reactflow';
import { Canvas } from '@/components/Canvas';
import { ChatPanel } from '@/components/ChatPanel';
import { Toolbar } from '@/components/Toolbar';
import { ToastContainer } from '@/components/Toast';
import { useToasts } from '@/hooks/useToasts';

const Index = () => {
  const { toasts, addToast, removeToast } = useToasts();

  // Resizable chat panel state
  const [chatWidth, setChatWidth] = useState<number>(() => {
    const stored = localStorage.getItem('chatWidth');
    const parsed = stored ? parseInt(stored, 10) : 480;
    return isNaN(parsed) ? 480 : parsed;
  });
  const isResizingRef = useRef(false);
  const startXRef = useRef(0);
  const startWidthRef = useRef(0);

  const CHAT_MIN = 360;
  const CHAT_MAX = 960;

  const onChatResizerMouseDown = (e: React.MouseEvent) => {
    isResizingRef.current = true;
    startXRef.current = e.clientX;
    startWidthRef.current = chatWidth;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';
  };

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (!isResizingRef.current) return;
      const delta = startXRef.current - e.clientX; // dragging left shrinks chat
      const next = Math.max(CHAT_MIN, Math.min(CHAT_MAX, startWidthRef.current + delta));
      setChatWidth(next);
    };
    const onMouseUp = () => {
      if (!isResizingRef.current) return;
      isResizingRef.current = false;
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
      try { localStorage.setItem('chatWidth', String(chatWidth)); } catch {}
    };
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [chatWidth]);

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Toolbar onToast={addToast} />
      
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-hidden">
          <ReactFlowProvider>
            <Canvas />
          </ReactFlowProvider>
        </div>
        {/* Vertical resizer between canvas and chat */}
        <div
          onMouseDown={onChatResizerMouseDown}
          className="relative w-[3px] bg-border hover:bg-primary/40 cursor-col-resize"
          title="Drag to resize chat"
        >
          <div className="absolute inset-y-0 -left-1 -right-1" />
        </div>
        <div className="overflow-hidden" style={{ width: chatWidth, minWidth: CHAT_MIN }}>
          <ChatPanel onToast={addToast} />
        </div>
      </div>

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
};

export default Index;
