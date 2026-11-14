import { validateProfile, type BuyerProfile } from './recommendation.ts';

// Una base existente también puede contener perfiles de un esquema anterior.
export function parseStoredProfile(value: string | null): BuyerProfile | null {
  if (!value || value.length > 16384) return null;
  try {
    const result = validateProfile(JSON.parse(value));
    return result.valid ? result.value : null;
  } catch { return null; }
}
