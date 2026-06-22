import { QueryClient } from '@tanstack/react-query';

/** Shared react-query client. Polling cadence is set per-query in the hooks. */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 1000,
    },
  },
});
