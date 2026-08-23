"use client";

export function LoadingSkeleton({ rows = 3 }: { rows?: number }) { return <div className="skeleton" aria-label="Loading">{Array.from({ length: rows }, (_, index) => <i key={index}/>)}</div>; }
export function EmptyState({ title, message }: { title: string; message: string }) { return <section className="stateCard"><span>○</span><h2>{title}</h2><p>{message}</p></section>; }
export function ErrorState({ message, retry }: { message: string; retry?: () => void }) { return <section className="stateCard error" role="alert"><span>!</span><h2>Unable to load this view</h2><p>{message}</p>{retry && <button onClick={retry}>Try again</button>}</section>; }
