import { InspectorCodePanel } from "./InspectorCodePanel";

interface QuerySpecPanelProps {
  value: unknown;
}

export function QuerySpecPanel({ value }: QuerySpecPanelProps) {
  return (
    <InspectorCodePanel
      title="QuerySpec JSON"
      language="json"
      content={value ? JSON.stringify(value) : ""}
      emptyText="QuerySpec is not available yet."
    />
  );
}
