'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DropZone from '@/components/DropZone';
import ProcessingStatus from '@/components/ProcessingStatus';
import { Card } from '@/components/ui/card';

export default function Home() {
  const router = useRouter();
  const [uploading, setUploading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFileAccepted = async (file: File) => {
    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/documents/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setJobId(data.job_id);
      setStep(1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setUploading(false);
    }
  };

  const handleProcessingComplete = (completedJobId: string) => {
    router.push(`/results/${completedJobId}`);
  };

  if (jobId) {
    return (
      <div className="flex flex-col flex-1 items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-black dark:to-slate-900 min-h-screen">
        <div className="w-full max-w-2xl px-4 py-8">
          <Card className="p-8">
            <h1 className="text-3xl font-bold mb-2">Processing Your Document</h1>
            <p className="text-muted-foreground mb-8">
              Your document is being processed. We'll extract the information shortly.
            </p>
            <ProcessingStatus 
              jobId={jobId} 
              step={step} 
              setStep={setStep}
              onComplete={handleProcessingComplete}
            />
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-black dark:to-slate-900 min-h-screen">
      <div className="w-full max-w-2xl px-4 py-8">
        <Card className="p-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Document OCR & Extraction</h1>
            <p className="text-muted-foreground text-lg">
              Upload your degree certificate or academic document to extract structured information automatically.
            </p>
          </div>

          <DropZone onFileAccepted={handleFileAccepted} />

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {uploading && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-800">Uploading file...</p>
            </div>
          )}

          <div className="mt-8 pt-8 border-t">
            <h2 className="text-lg font-semibold mb-4">Supported Formats</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>✓ PDF documents (up to 10MB)</li>
              <li>✓ JPEG images (up to 10MB)</li>
              <li>✓ PNG images (up to 10MB)</li>
              <li>✓ Multi-page documents automatically split and processed</li>
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
}

