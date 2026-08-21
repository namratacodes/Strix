interface FogLayerProps {
  tint: "danger" | "toxic";
}

const TINT_RGBA: Record<FogLayerProps["tint"], string> = {
  danger: "rgba(255,59,59,0.18)",
  toxic: "rgba(57,255,136,0.18)",
};

export default function FogLayer({ tint }: FogLayerProps) {
  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden">
      <video
        className="h-full w-full object-cover opacity-70"
        src="/videos/fog-background.mp4"
        autoPlay
        muted
        loop
        playsInline
      />
      <div
        className="absolute inset-0 transition-colors duration-1000"
        style={{ background: TINT_RGBA[tint] }}
      />
    </div>
  );
}