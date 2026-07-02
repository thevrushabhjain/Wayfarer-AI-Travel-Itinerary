export function GridBackground() {
  return (
    <div
      data-testid="grid-background"
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 bg-grid bg-grid-fade"
    />
  );
}
