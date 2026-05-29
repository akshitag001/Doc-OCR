"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function Error({ error }: { error: Error & { digest?: string } }) {
  const router = useRouter();

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-md text-center space-y-4">
        <h1 className="text-2xl font-semibold">Something went wrong processing your document</h1>
        <p className="text-muted-foreground">{error.message || "Please try again."}</p>
        <Button onClick={() => router.push("/")}>Try again</Button>
      </div>
    </div>
  );
}
