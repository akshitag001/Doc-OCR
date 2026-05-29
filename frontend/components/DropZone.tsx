"use client";
import { useRef, useState } from 'react';
import { UploadButton } from './UploadButton';
import { FileIcon, FileText, FileImage } from 'lucide-react';

const ACCEPTED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
const MAX_SIZE_MB = 10;

export default function DropZone({ onFileAccepted }: { onFileAccepted: (file: File) => void }) {
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setError(null);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    validateAndAccept(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const file = e.target.files?.[0];
    if (!file) return;
    validateAndAccept(file);
  };

  const validateAndAccept = (file: File) => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError('Unsupported format');
      return;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setError('File too large');
      return;
    }
    setFileName(file.name);
    onFileAccepted(file);
  };

  return (
    <div
      className="border-2 border-dashed border-muted rounded-lg p-8 flex flex-col items-center justify-center gap-4 bg-card shadow-sm"
      onDrop={handleDrop}
      onDragOver={e => e.preventDefault()}
    >
      <div className="flex flex-col items-center gap-2">
        {fileName ? (
          <FileText className="w-8 h-8 text-primary" />
        ) : (
          <FileIcon className="w-8 h-8 text-muted-foreground" />
        )}
        <span className="text-lg font-medium">{fileName || 'Drag & drop your document here'}</span>
      </div>
      <UploadButton inputRef={inputRef} onChange={handleChange} />
      {error && <span className="text-red-500 text-sm mt-2">{error}</span>}
      <input ref={inputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden" onChange={handleChange} />
    </div>
  );
}
