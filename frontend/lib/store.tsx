"use client";

/*
 * Global client state: identity (discord_id), profile, and toast feed.
 * All game data flows through here — screens stay dumb.
 */
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { api, ApiError, Profile } from "./api";

const DID_KEY = "anromi_discord_id";

export interface Toast {
  id: number;
  text: string;
  ok: boolean;
}

interface StoreValue {
  did: string | null;
  ready: boolean;
  offline: boolean;
  enter: (discordId: string) => void;
  logout: () => void;
  profile: Profile | null;
  refreshProfile: () => Promise<Profile | null>;
  toasts: Toast[];
  pushToast: (text: string, ok?: boolean) => void;
  /** Runs an API call; auto-toasts `.message` results and errors. Returns null on failure. */
  act: <T extends { message?: string }>(fn: () => Promise<T>) => Promise<T | null>;
}

const Ctx = createContext<StoreValue | null>(null);

export function StoreProvider({ children }: { children: React.ReactNode }) {
  const [did, setDid] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [offline, setOffline] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const toastSeq = useRef(0);

  useEffect(() => {
    const saved = typeof window !== "undefined" ? localStorage.getItem(DID_KEY) : null;
    if (saved) setDid(saved);
    setReady(true);
  }, []);

  const pushToast = useCallback((text: string, ok = true) => {
    const id = ++toastSeq.current;
    setToasts((t) => [...t.slice(-4), { id, text, ok }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 7000);
  }, []);

  const refreshProfile = useCallback(async (): Promise<Profile | null> => {
    if (!did) return null;
    try {
      const p = await api.profile(did);
      setProfile(p);
      setOffline(false);
      return p;
    } catch (ex) {
      if (ex instanceof ApiError && ex.status === 404) {
        // not registered yet — register silently so the flow never blocks
        try {
          const p = await api.register(did, `Cultivator_${did.slice(-4)}`);
          setProfile(p);
          setOffline(false);
          return p;
        } catch (regEx) {
          if (!(regEx instanceof ApiError)) setOffline(true);
          return null;
        }
      }
      // network / CORS / server down
      setOffline(true);
      return null;
    }
  }, [did]);

  useEffect(() => {
    if (!did) return;
    refreshProfile();
    const t = setInterval(refreshProfile, 15000);
    return () => clearInterval(t);
  }, [did, refreshProfile]);

  // Bridge for imperative toast pushes from deep components (CustomEvents)
  useEffect(() => {
    const handler = (e: Event) => {
      const d = (e as CustomEvent).detail as { msg?: string; ok?: boolean };
      if (d?.msg) pushToast(d.msg, d.ok ?? true);
    };
    window.addEventListener("anromi-toast", handler);
    return () => window.removeEventListener("anromi-toast", handler);
  }, [pushToast]);

  const value = useMemo<StoreValue>(
    () => ({
      did,
      ready,
      offline,
      enter: (id) => {
        localStorage.setItem(DID_KEY, id);
        setDid(id);
      },
      logout: () => {
        localStorage.removeItem(DID_KEY);
        setDid(null);
        setProfile(null);
      },
      profile,
      refreshProfile,
      toasts,
      pushToast,
      act: async (fn) => {
        try {
          const res = await fn();
          if (res?.message) pushToast(res.message, true);
          refreshProfile();
          return res;
        } catch (ex) {
          const msg = ex instanceof ApiError ? ex.message : "The heavens are unreachable...";
          pushToast(msg, false);
          return null;
        }
      },
    }),
    [did, ready, profile, toasts, pushToast, refreshProfile]
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useStore(): StoreValue {
  const v = useContext(Ctx);
  if (!v) throw new Error("useStore must be used inside <StoreProvider>");
  return v;
}
