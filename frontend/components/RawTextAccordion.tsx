import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';

export default function RawTextAccordion({ rawText }: { rawText?: string }) {
  const [open, setOpen] = useState(false);
  if (!rawText) return null;
  return (
    <Card className="p-4 mt-4">
      <Button variant="ghost" onClick={() => setOpen(o => !o)}>
        {open ? 'Hide Raw Text' : 'Show Raw Text'}
      </Button>
      {open && <pre className="mt-2 whitespace-pre-wrap text-sm bg-muted p-2 rounded">{rawText}</pre>}
    </Card>
  );
}
