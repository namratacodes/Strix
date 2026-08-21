import { motion } from "framer-motion";

export default function Authors() {
  return (
    <section className="relative bg-background bg-grid-dots px-6 py-28">
      <div className="mx-auto max-w-2xl text-center">
        <motion.h2
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.5 }}
          className="font-display text-3xl font-normal tracking-wide text-white"
        >
          Built by
        </motion.h2>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="mx-auto mt-10 flex max-w-sm flex-col items-center rounded-2xl border border-white/10 bg-white/5 p-8"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/15 text-lg font-medium text-primary-light">
            N
          </div>

          <p className="mt-4 text-base font-medium text-white">Namrata</p>

          <p className="text-sm text-white/50">
            Creator &amp; Developer
          </p>

          <a
            href="https://github.com/namratacodes/Strix"
            target="_blank"
            rel="noreferrer"
            className="mt-4 rounded-lg border border-white/15 px-4 py-1.5 text-xs text-white/70 transition-colors hover:bg-white/10"
          >
            View on GitHub
          </a>
        </motion.div>
      </div>
    </section>
  );
}