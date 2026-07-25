export function Footer() {
  return (
    <footer className="w-full border-t border-ink-900/10 bg-cream-50/80 py-6 text-center text-sm text-ink-700 backdrop-blur-sm">
      <p>
        Built for{" "}
        <a
          href="https://digitalheroesco.com"
          target="_blank"
          rel="noopener noreferrer"
          className="font-semibold text-amber-650 underline decoration-amber-650/30 underline-offset-4 transition-colors hover:text-ink-900 hover:decoration-ink-900/40"
        >
          Digital Heroes Training Task
        </a>
      </p>
    </footer>
  );
}
