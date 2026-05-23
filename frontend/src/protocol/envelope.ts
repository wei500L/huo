export interface Envelope<T> {
  v: 1;
  id: string;
  ts: string;
  direction: "inbound" | "outbound";
  type: string;
  ackFor?: string;
  payload: T;
}

export const makeEnvelope = <T>(type: string, payload: T, ackFor?: string): Envelope<T> => ({
  v: 1,
  id: crypto.randomUUID(),
  ts: new Date().toISOString(),
  direction: "inbound",
  type,
  ackFor,
  payload,
});
