import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** shadcn/ui class-merge helper — used by the ported aceternity/magicui islands. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
