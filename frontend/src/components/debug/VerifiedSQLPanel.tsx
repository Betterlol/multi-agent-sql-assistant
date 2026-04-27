import { InspectorCodePanel } from "./InspectorCodePanel";

interface VerifiedSQLPanelProps {
  sql?: string | null;
}

export function VerifiedSQLPanel({ sql }: VerifiedSQLPanelProps) {
  return (
    <InspectorCodePanel
      title="Verified SQL"
      language="sql"
      content={sql ?? ""}
      emptyText="No verified SQL yet."
    />
  );
}
