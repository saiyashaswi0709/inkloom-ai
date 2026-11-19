/**
 * Date & Timezone utilities for Inkloom AI
 * Configured for Asia/Kolkata (IST, UTC+05:30)
 */

export const DEFAULT_TIMEZONE = 'Asia/Kolkata';

/**
 * Safely parses any date string, timestamp or Date instance into a Date object.
 * If an ISO date string lacks a timezone indicator (Z or +/-offset), it appends 'Z'
 * to guarantee it is interpreted as UTC, protecting historical records.
 */
export function parseUtcDate(dateInput: string | number | Date | null | undefined): Date {
  if (!dateInput) return new Date();
  if (dateInput instanceof Date) return dateInput;

  let str = String(dateInput).trim();
  // If ISO string like '2026-11-18T17:34:00' lacks timezone, append Z so it is parsed as UTC
  if (str.includes('T') && !str.endsWith('Z') && !/[+-]\d{2}(:\d{2})?$/.test(str)) {
    str += 'Z';
  }
  const parsed = new Date(str);
  return isNaN(parsed.getTime()) ? new Date() : parsed;
}

/**
 * Formats time in IST (e.g., '11:04 PM' or '11:04 pm')
 */
export function formatTimeIST(dateInput: string | number | Date | null | undefined): string {
  const date = parseUtcDate(dateInput);
  return date.toLocaleTimeString('en-IN', {
    timeZone: DEFAULT_TIMEZONE,
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

/**
 * Formats date in IST (e.g., '18 Nov 2026')
 */
export function formatDateIST(dateInput: string | number | Date | null | undefined): string {
  const date = parseUtcDate(dateInput);
  return date.toLocaleDateString('en-IN', {
    timeZone: DEFAULT_TIMEZONE,
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

/**
 * Formats full date and time in IST (e.g., '18 Nov 2026, 11:04 pm')
 */
export function formatDateTimeIST(dateInput: string | number | Date | null | undefined): string {
  const date = parseUtcDate(dateInput);
  return date.toLocaleString('en-IN', {
    timeZone: DEFAULT_TIMEZONE,
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}
