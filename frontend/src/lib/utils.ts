import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export const TypedObject = {
	keys<T extends object>(obj: T): string[] {
		return Object.keys(obj);
	}
};
