import { Card } from './ui/card';
import { Badge } from './ui/badge';

function getBadgeColor(confidence: number) {
  if (confidence >= 85) return 'bg-green-500';
  if (confidence >= 60) return 'bg-yellow-400';
  return 'bg-red-500';
}

export default function ExtractionCard({ label, value, confidence }: { label: string, value?: string, confidence?: number }) {
  return (
    <Card className="p-4 flex items-center justify-between mb-2">
      <div>
        <div className="font-medium text-sm text-muted-foreground">{label}</div>
        <div className="text-lg font-semibold">{value || <span className="text-muted-foreground">—</span>}</div>
      </div>
      {confidence !== undefined && (
        <Badge className={getBadgeColor(confidence) + ' text-white'}>{confidence}%</Badge>
      )}
    </Card>
  );
}
