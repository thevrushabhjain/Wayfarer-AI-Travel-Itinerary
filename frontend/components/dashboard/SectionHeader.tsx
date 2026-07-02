export function SectionHeader({
  overline,
  title,
  testId,
}: {
  overline: string;
  title: string;
  testId?: string;
}) {
  return (
    <div data-testid={testId} className="mb-5 space-y-1">
      <p className="font-mono text-xs uppercase tracking-widest text-zinc-500">{overline}</p>
      <h2 className="text-2xl font-medium tracking-tight text-zinc-50 sm:text-3xl">{title}</h2>
    </div>
  );
}
