const statusColors: Record<string, string> = {
  blocked: 'bg-rose-500/15 text-rose-700 border-rose-500/30',
  done: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
  in_progress: 'bg-sky-500/15 text-sky-700 border-sky-500/30',
  todo: 'bg-slate-500/10 text-slate-600 border-slate-500/20',
};

const priorityColors: Record<string, string> = {
  critical: 'bg-rose-500 text-white',
  high: 'bg-orange-500 text-white',
  low: 'bg-emerald-500 text-white',
  medium: 'bg-indigo-500 text-white',
};

export { priorityColors, statusColors };
