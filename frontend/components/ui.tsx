"use client";

import React from "react";

export function Panel({
  title,
  children,
  className = "",
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel p-4 ${className}`}>
      {title && (
        <header className="mb-3">
          <h2 className="font-display text-gold tracking-wide text-sm uppercase">{title}</h2>
          <div className="gold-rule mt-1.5" />
        </header>
      )}
      {children}
    </section>
  );
}

export function Bar({
  label,
  value,
  max,
  tone = "jade",
  suffix,
}: {
  label: string;
  value: number;
  max: number;
  tone?: "jade" | "gold" | "blood" | "soul";
  suffix?: string;
}) {
  const pct = Math.max(0, Math.min(100, (value / Math.max(1, max)) * 100));
  const tones: Record<string, string> = {
    jade: "bg-jade",
    gold: "bg-gold",
    blood: "bg-blood",
    soul: "bg-soul",
  };
  return (
    <div>
      <div className="flex justify-between text-xs text-mist mb-1">
        <span>{label}</span>
        <span className="text-parchment">
          {Number.isInteger(value) ? value : value.toFixed(1)}
          {suffix ?? ` / ${max > 999999 ? `${(max / 1e6).toFixed(0)}M` : max}`}
        </span>
      </div>
      <div className="h-2 rounded-full bg-ink-700 overflow-hidden">
        <div
          className={`h-full rounded-full ${tones[tone]} transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

const BTN_TONES: Record<string, string> = {
  gold: "bg-gold/15 border-gold text-gold hover:bg-gold/25",
  jade: "bg-jade/15 border-jade text-jade hover:bg-jade/25",
  blood: "bg-blood/15 border-blood text-red-300 hover:bg-blood/30",
  soul: "bg-soul/15 border-soul text-soul hover:bg-soul/25",
  ghost: "bg-transparent border-mist/40 text-mist hover:text-parchment hover:border-mist",
};

export function Btn({
  children,
  onClick,
  tone = "gold",
  disabled,
  className = "",
  title,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  tone?: "gold" | "jade" | "blood" | "soul" | "ghost";
  disabled?: boolean;
  className?: string;
  title?: string;
}) {
  return (
    <button
      title={title}
      disabled={disabled}
      onClick={onClick}
      className={`btn-action px-4 py-2 rounded-lg border text-sm font-medium ${BTN_TONES[tone]} ${className}`}
    >
      {children}
    </button>
  );
}

export function Chip({
  label,
  value,
  tone = "mist",
}: {
  label: string;
  value: React.ReactNode;
  tone?: "mist" | "gold" | "jade" | "blood" | "soul";
}) {
  const tones: Record<string, string> = {
    mist: "text-mist",
    gold: "text-gold",
    jade: "text-jade",
    blood: "text-red-400",
    soul: "text-soul",
  };
  return (
    <div className="flex items-center justify-between gap-3 py-1.5 border-b border-ink-700 last:border-0">
      <span className="text-xs text-mist">{label}</span>
      <span className={`text-sm font-medium ${tones[tone]}`}>{value}</span>
    </div>
  );
}

export function Empty({ text }: { text: string }) {
  return <p className="text-mist text-sm italic py-4 text-center">{text}</p>;
}
