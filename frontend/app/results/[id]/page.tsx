"use client";

import { useEffect, useState } from "react";
import DocumentPreview from "../../../components/DocumentPreview";
import ExtractionCard from "../../../components/ExtractionCard";
import RawTextAccordion from "../../../components/RawTextAccordion";
import ExportButton from "../../../components/ExportButton";
import { Skeleton } from "../../../components/ui/skeleton";

type ExtractionResult = {
  id: string;
  status: string;
  filename: string;
  documentType?: string;
  holder: { name?: string; fatherName?: string; dob?: string };
  credential: { degree?: string; institution?: string; year?: string; cgpa?: string };
  issuer: { name?: string };
  confidence: Record<string, number>;
  rawText?: string;
  errorMessage?: string | null;
};

function getDocumentTypeIcon(docType?: string) {
  const key = (docType || "UNKNOWN").toUpperCase().replace(/\s+/g, "_");
  const map: Record<string, string> = {
    AADHAAR: "🪪",
    PASSPORT: "🛂",
    DEGREE_CERTIFICATE: "🎓",
    MARKSHEET: "📋",
    DRIVING_LICENSE: "🚗",
    UNKNOWN: "📄",
  };
  return map[key] || "📄";
}

export default function ResultsPage({ params }: { params: { id: string } }) {
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    let interval: NodeJS.Timeout | null = null;

    const fetchResult = async () => {
      try {
        const res = await fetch(`/api/documents/${params.id}/result`);
        if (!res.ok) {
          const payload = await res.json().catch(() => ({}));
          throw new Error(payload?.error || "Failed to fetch result");
        }
        const data = await res.json();
        if (isMounted) {
          setResult(data);
          const isPending = data.status === "pending" || data.status === "processing";
          setLoading(isPending);
          if (!isPending && interval) {
            clearInterval(interval);
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to fetch result");
          setLoading(false);
        }
      }
    };

    fetchResult();
    interval = setInterval(fetchResult, 2000);
    return () => {
      isMounted = false;
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [params.id]);

  if (error) {
    const isNotFound = error.toLowerCase().includes("job not found");
    return (
      <div className="p-6">
        <div className="text-red-600 font-medium">
          {isNotFound ? "Job not found" : error}
        </div>
        {isNotFound && (
          <div className="text-muted-foreground">
            Please upload the document again to generate a new job.
          </div>
        )}
      </div>
    );
  }

  if (!loading && result?.status === "failed") {
    return (
      <div className="p-6">
        <div className="text-red-600 font-medium">Something went wrong processing your document</div>
        <div className="text-muted-foreground">{result.errorMessage || "Please try again."}</div>
      </div>
    );
  }

  const icon = getDocumentTypeIcon(result?.documentType);

  return (
    <div className="flex flex-col md:flex-row gap-8 p-6">
      <div className="md:w-1/3">
        <DocumentPreview />
      </div>
      <div className="flex-1 space-y-6">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{icon}</span>
          <h1 className="text-2xl font-semibold">
            {result?.documentType || "Document"}
          </h1>
        </div>

        {loading ? (
          <div className="space-y-4">
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
          </div>
        ) : (
          result && (
            <>
              <section>
                <h2 className="font-bold text-lg mb-2">Holder Info</h2>
                <ExtractionCard label="Full Name" value={result.holder?.name} confidence={result.confidence?.name} />
                <ExtractionCard label="Father's Name" value={result.holder?.fatherName} confidence={result.confidence?.fatherName} />
                <ExtractionCard label="Date of Birth" value={result.holder?.dob} confidence={result.confidence?.dob} />
              </section>
              <section>
                <h2 className="font-bold text-lg mb-2">Credential Info</h2>
                <ExtractionCard label="Degree" value={result.credential?.degree} confidence={result.confidence?.degree} />
                <ExtractionCard label="Institution" value={result.credential?.institution} confidence={result.confidence?.institution} />
                <ExtractionCard label="Year" value={result.credential?.year} confidence={result.confidence?.year} />
                <ExtractionCard label="CGPA" value={result.credential?.cgpa} confidence={result.confidence?.cgpa} />
              </section>
              <section>
                <h2 className="font-bold text-lg mb-2">Issuer Info</h2>
                <ExtractionCard label="Issuer" value={result.issuer?.name} confidence={result.confidence?.issuer} />
              </section>
              <RawTextAccordion rawText={result.rawText || ""} />
              <ExportButton data={result} />
            </>
          )
        )}
      </div>
    </div>
  );
}
