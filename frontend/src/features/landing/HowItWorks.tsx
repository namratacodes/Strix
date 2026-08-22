import { motion } from "framer-motion";

const steps = [
  {
    tag: "Step 1",
    title: "Paste your code",
    description: "Drop Python code into the editor.No setup, no account needed to try it.",
  },
  {
    tag: "Step 2",
    title: "STRIX analyzes deterministically",
    description: "Static AST analysis finds loops, recursion, and structure facts, not guesses.",
  },
  {
    tag: "Step 3",
    title: "Get an explained result",
    description: "See the algorithm, complexity, and a step by step reasoning timeline behind it.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="relative bg-background bg-grid-dots px-6 py-28">
      <div className="mx-auto max-w-5xl text-center">
        <motion.h2
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.5 }}
          className="font-display text-3xl font-normal tracking-wide text-white"
        >
          How it works
        </motion.h2>
        <p className="mx-auto mt-3 max-w-md text-sm text-white/50">
          Three steps between your code and understanding why it works the way it does.
        </p>

        <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-3">
          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ duration: 0.5, delay: i * 0.12 }}
              className="rounded-2xl border border-white/10 bg-white/5 p-6 text-left"
            >
              <span className="font-mono text-xs text-primary-light">{step.tag}</span>
              <h3 className="mt-3 text-lg font-medium text-white">{step.title}</h3>
              <p className="mt-2 text-sm text-white/50">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}