import { InspectorCodePanel } from "./InspectorCodePanel";

interface BuiltSQLPanelProps {
  sql?: string | null;
}

export function BuiltSQLPanel({ sql }: BuiltSQLPanelProps) {
  return <InspectorCodePanel title="Built SQL" language="sql" content={sql ?? ""} emptyText="No built SQL yet." />;
}
