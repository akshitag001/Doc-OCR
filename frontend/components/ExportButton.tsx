import { Button } from './ui/button';
import { Copy } from 'lucide-react';
import { toast } from 'sonner';

export default function ExportButton({ data }: { data: any }) {
  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    toast.success("Copied to clipboard!");
  };
  return (
    <Button variant="outline" onClick={handleCopy} className="flex items-center gap-2 mt-2">
      <Copy className="w-4 h-4" /> Copy JSON
    </Button>
  );
}
