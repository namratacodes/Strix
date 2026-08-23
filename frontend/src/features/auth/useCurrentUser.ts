import { useQuery } from "@tanstack/react-query";
import { fetchCurrentUser } from "./api";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],
    queryFn: fetchCurrentUser,
    retry: false,
  });
}