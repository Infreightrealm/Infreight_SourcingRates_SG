/**
 * useRateSearch — drives the create-then-poll flow against the backend.
 *
 * Mirrors the web client's pollRateSearch loop, but using react-query's
 * refetchInterval so it auto-stops on a terminal status and pauses in the
 * background.
 */
import { useCallback, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

import {
  createRateSearch,
  getRateSearchResults,
  releaseRateSearch,
} from '@/services/api';
import type { RateSearchRequest, RateSearchResultResponse } from '@/types/api';
import { TERMINAL_STATUSES } from '@/types/api';

const POLL_MS = 2500;

function isTerminal(status?: string): boolean {
  return !!status && (TERMINAL_STATUSES as readonly string[]).includes(status);
}

export function useRateSearch() {
  const [searchId, setSearchId] = useState<string | null>(null);

  const create = useMutation({
    mutationFn: (req: RateSearchRequest) => createRateSearch(req),
    onSuccess: (data) => setSearchId(data.search_id),
  });

  const poll = useQuery<RateSearchResultResponse>({
    queryKey: ['rate-search', searchId],
    queryFn: () => getRateSearchResults(searchId as string),
    enabled: !!searchId,
    refetchInterval: (query) =>
      isTerminal(query.state.data?.status) ? false : POLL_MS,
    refetchIntervalInBackground: false,
  });

  const reset = useCallback(() => {
    if (searchId) {
      releaseRateSearch(searchId).catch(() => {
        /* best-effort lock release */
      });
    }
    setSearchId(null);
    create.reset();
  }, [searchId, create]);

  const status = poll.data?.status;

  return {
    searchId,
    result: poll.data ?? null,
    status,
    isCreating: create.isPending,
    isPolling: !!searchId && !isTerminal(status),
    error: (create.error as Error | null) ?? (poll.error as Error | null),
    start: (req: RateSearchRequest) => create.mutate(req),
    reset,
  };
}
