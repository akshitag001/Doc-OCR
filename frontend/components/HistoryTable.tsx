"use client";

import { useEffect, useState } from "react";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import Link from "next/link";
import { toast } from "sonner";

type HistoryItem = {
  id: string;
  filename: string;
  documentType?: string;
  createdAt?: string;
  status: string;
};

function statusColor(status: string) {
  if (status === 'completed') return 'bg-green-500';
  if (status === 'processing') return 'bg-yellow-400';
  return 'bg-gray-400';
}

export default function HistoryTable() {
  const [docs, setDocs] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const res = await fetch("/api/documents");
        const data = await res.json();
        setDocs(data || []);
      } catch (error) {
        toast.error("Failed to load history");
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, []);

  const handleDelete = async (id: string) => {
    try {
      const res = await fetch(`/api/documents/${id}`, { method: "DELETE" });
      if (!res.ok && res.status !== 204) {
        throw new Error("Delete failed");
      }
      setDocs(prev => prev.filter(doc => doc.id !== id));
      toast.success("Document deleted");
    } catch (error) {
      toast.error("Failed to delete document");
    }
  };

  if (!loading && docs.length === 0) {
    return (
      <Card className="p-8 flex flex-col items-center justify-center">
        <span className="text-muted-foreground">No documents processed yet.</span>
      </Card>
    );
  }
  return (
    <div className="grid gap-4">
      {docs.map(doc => (
        <Card key={doc.id} className="p-4 flex items-center justify-between">
          <div>
            <div className="font-medium">{doc.filename}</div>
            <div className="text-sm text-muted-foreground">{doc.documentType || "Unknown"}</div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">{doc.createdAt?.slice(0, 10) || "-"}</span>
            <Badge className={statusColor(doc.status) + ' text-white'}>{doc.status}</Badge>
            <Link href={`/results/${doc.id}`} className="underline text-primary">View Results</Link>
            <Button variant="outline" size="sm" onClick={() => handleDelete(doc.id)}>Delete</Button>
          </div>
        </Card>
      ))}
    </div>
  );
}
