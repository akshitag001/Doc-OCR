"use client";
import { useEffect, useState } from 'react';
import { Progress } from './ui/progress';
import { CheckCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const steps = [
  { label: 'Uploading file...' },
  { label: 'Preprocessing image...' },
  { label: 'Running OCR...' },
  { label: 'Extracting structured data...' },
  { label: 'Done!' },
];

interface ProcessingStatusProps {
  jobId: string;
  step: number;
  setStep: (n: number) => void;
  onComplete?: (jobId: string) => void;
}

export default function ProcessingStatus({ jobId, step, setStep, onComplete }: ProcessingStatusProps) {
  const [status, setStatus] = useState('pending');

  useEffect(() => {
    if (!jobId) return;
    if (step >= steps.length - 1) return;
    
    const interval = setInterval(async () => {
      try {
        // Poll backend for status
        const res = await fetch(`/api/documents/${jobId}/result`);
        
        if (!res.ok) {
          console.error('Failed to fetch status:', res.status);
          if (res.status === 404) {
            setStep(steps.length - 1);
            clearInterval(interval);
            toast.error("Job not found. Please upload again.");
          }
          return;
        }
        
        const data = await res.json();
        setStatus(data.status);
        
        if (data.status === 'completed') {
          setStep(steps.length - 1);
          clearInterval(interval);
          toast.success("Processing complete");
          
          // Call onComplete callback if provided
          if (onComplete) {
            setTimeout(() => onComplete(jobId), 1000);
          }
        } else if (data.status === 'failed') {
          setStep(steps.length - 1);
          clearInterval(interval);
          toast.error(data.errorMessage || "Processing failed");
        } else {
          // Progress to next step
          setStep(Math.min(step + 1, steps.length - 2));
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [jobId, step, setStep, onComplete]);

  return (
    <div className="space-y-6">
      {steps.map((s, i) => (
        <div key={i} className="flex items-center gap-3">
          {i < step ? (
            <CheckCircle className="text-green-500 w-5 h-5" />
          ) : i === step ? (
            <Loader2 className="animate-spin text-blue-500 w-5 h-5" />
          ) : (
            <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
          )}
          <span className={i < step ? 'text-green-600 font-medium' : i === step ? 'text-blue-600 font-medium' : 'text-gray-500'}>
            {s.label}
          </span>
        </div>
      ))}
      <Progress value={(step / steps.length) * 100} className="mt-4" />
    </div>
  );
}
