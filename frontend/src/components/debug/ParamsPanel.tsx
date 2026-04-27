import { InspectorCodePanel } from "./InspectorCodePanel";

interface ParamsPanelProps {
  params?: unknown[] | null;
}

export function ParamsPanel({ params }: ParamsPanelProps) {
  return (
    <InspectorCodePanel
      title="SQL Params"
      language="json"
      content={JSON.stringify(params ?? [])}
      emptyText="No SQL params yet."
    />
  );
}
