export interface ExtractionResult {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  holder: { name?: string; fatherName?: string; dob?: string };
  credential: { degree?: string; institution?: string; year?: string; cgpa?: string };
  issuer: { name?: string };
  confidence: Record<string, number>;
  rawText?: string;
  documentType?: string;
  createdAt: string;
}
