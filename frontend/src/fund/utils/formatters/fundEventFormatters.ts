/**
 * Fund event display helpers.
 *
 * Provides color mapping utilities that drive shared chip components and
 * legacy views during the migration window.
 */

import type { EventType } from '@/fund/types';
import {
  EVENT_TYPE_COLORS,
  type EventDisplayColor,
} from '@/fund/utils/constants/fundDisplayConfig';

/**
 * Map a fund event type to the design-system color token used by chips/cards.
 *
 * @param eventType - Raw event type string or enum value received from the API.
 * @returns Material UI color token consumed by chip variants.
 */
export const getEventTypeColor = (
  eventType: EventType | string
): EventDisplayColor => {
  const normalizedType = eventType?.toString().toUpperCase();

  return EVENT_TYPE_COLORS[normalizedType] ?? 'default';
};

