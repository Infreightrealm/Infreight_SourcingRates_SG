/**
 * Auth store (zustand) with persistence.
 *
 * The backend uses lightweight, name-only auth (no token), so we persist just
 * the resolved user. On native we use the OS keychain via expo-secure-store; on
 * web we fall back to localStorage (SecureStore is unsupported there).
 */
import { create } from 'zustand';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const STORAGE_KEY = 'infreight.user';

const storage = {
  async get(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      return globalThis.localStorage?.getItem(key) ?? null;
    }
    return SecureStore.getItemAsync(key);
  },
  async set(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      globalThis.localStorage?.setItem(key, value);
      return;
    }
    await SecureStore.setItemAsync(key, value);
  },
  async remove(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      globalThis.localStorage?.removeItem(key);
      return;
    }
    await SecureStore.deleteItemAsync(key);
  },
};

export interface AuthUser {
  id: string;
  name: string;
}

interface AuthState {
  user: AuthUser | null;
  /** True once the persisted user has been read from storage at startup. */
  hydrated: boolean;
  hydrate: () => Promise<void>;
  login: (user: AuthUser) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  hydrated: false,
  hydrate: async () => {
    try {
      const raw = await storage.get(STORAGE_KEY);
      set({ user: raw ? (JSON.parse(raw) as AuthUser) : null, hydrated: true });
    } catch {
      set({ user: null, hydrated: true });
    }
  },
  login: async (user) => {
    await storage.set(STORAGE_KEY, JSON.stringify(user));
    set({ user });
  },
  logout: async () => {
    await storage.remove(STORAGE_KEY);
    set({ user: null });
  },
}));
