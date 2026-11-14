import { timingSafeEqual } from 'node:crypto';
import { localAnalyticsRequest } from './analytics-validation.ts';

export function canReadAnalytics(request: Request, settings: { token?: string; localOnly?: boolean }) {
  if (!settings.token) return settings.localOnly === true && localAnalyticsRequest(request);
  const supplied = Buffer.from(request.headers.get('x-analytics-token') || '');
  const expected = Buffer.from(settings.token);
  return supplied.length === expected.length && timingSafeEqual(supplied, expected);
}
