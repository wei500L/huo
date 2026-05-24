export const deepClone = <T>(value: T): T => {
  if (typeof globalThis.structuredClone === "function") {
    return globalThis.structuredClone(value);
  }

  return JSON.parse(JSON.stringify(value)) as T;
};

export const clampText = (value: string, maxLength: number): string => {
  return value.length <= maxLength ? value : value.slice(0, maxLength);
};
