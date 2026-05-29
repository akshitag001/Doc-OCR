import Image from 'next/image';
import { Card } from './ui/card';

export default function DocumentPreview({ fileUrl }: { fileUrl?: string }) {
  return (
    <Card className="p-4 flex items-center justify-center h-64">
      {fileUrl ? (
        <Image src={fileUrl} alt="Document preview" width={200} height={260} className="object-contain max-h-60" />
      ) : (
        <div className="text-sm text-muted-foreground">Preview unavailable</div>
      )}
    </Card>
  );
}
