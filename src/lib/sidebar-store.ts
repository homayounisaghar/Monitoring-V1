import { useSyncExternalStore } from "react";

export const SIDEBAR_EXPANDED = 260;
export const SIDEBAR_COLLAPSED = 44;

let collapsed = false;
const listeners = new Set<() => void>();

function emit() {
  for (const l of listeners) l();
}

export function setSidebarCollapsed(next: boolean) {
  if (collapsed === next) return;
  collapsed = next;
  emit();
}

export function toggleSidebarCollapsed() {
  setSidebarCollapsed(!collapsed);
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => {
    listeners.delete(cb);
  };
}

function getSnapshot() {
  return collapsed;
}

function getServerSnapshot() {
  return false;
}

export function useSidebarCollapsed() {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

export function useSidebarWidth() {
  const c = useSidebarCollapsed();
  return c ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED;
}
