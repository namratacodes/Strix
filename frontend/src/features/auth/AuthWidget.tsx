import { useQueryClient } from "@tanstack/react-query";
import { loginUrl, logout } from "./api";
import { useCurrentUser } from "./useCurrentUser";

export default function AuthWidget() {
  const { data: user, isLoading } = useCurrentUser();
  const queryClient = useQueryClient();

  if (isLoading) return null;

  if (!user) {
    return (
      <a
        href={loginUrl()}
        className="rounded-lg border border-white/15 px-4 py-1.5 text-xs text-white/70 transition-colors hover:bg-white/10"
      >
        Sign in with Google
      </a>
    );
  }

  return (
    <div className="flex items-center gap-3 text-xs text-white/60">
      <span>{user.display_name}</span>

      <button
        onClick={async () => {
          await logout();
          queryClient.invalidateQueries({
            queryKey: ["current-user"],
          });
        }}
        className="rounded-lg border border-white/15 px-3 py-1 transition-colors hover:bg-white/10"
      >
        Sign out
      </button>
    </div>
  );
}