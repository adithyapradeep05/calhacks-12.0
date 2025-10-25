import { ReactFlowProvider } from 'reactflow';
import { Canvas } from '@/components/Canvas';
import { ChatPanel } from '@/components/ChatPanel';
import { Toolbar } from '@/components/Toolbar';
import { ToastContainer } from '@/components/Toast';
import { useToasts } from '@/hooks/useToasts';

const Index = () => {
  const { toasts, addToast, removeToast } = useToasts();

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Toolbar onToast={addToast} />
      
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-hidden">
          <ReactFlowProvider>
            <Canvas />
          </ReactFlowProvider>
        </div>
        
        <div className="w-[35%] overflow-hidden">
          <ChatPanel onToast={addToast} />
        </div>
      </div>

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
};

export default Index;
