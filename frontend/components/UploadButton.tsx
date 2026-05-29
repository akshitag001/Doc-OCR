"use client";
import { Button } from './ui/button';

export function UploadButton({ inputRef, onChange }: { inputRef: React.RefObject<HTMLInputElement | null>, onChange: (e: React.ChangeEvent<HTMLInputElement>) => void }) {
  return (
    <Button type="button" onClick={() => inputRef.current?.click()} className="mt-2">
      Browse File
      <input ref={inputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden" onChange={onChange} />
    </Button>
  );
}
