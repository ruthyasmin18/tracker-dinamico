interface Props {
  label: string
  current: number
  target: number
  unit?: string
  color?: string
}

export default function MacroBar({ label, current, target, unit = 'g', color = 'bg-brand-500' }: Props) {
  const pct = target > 0 ? Math.min((current / target) * 100, 100) : 0
  const over = current > target

  return (
    <div>
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-sm font-medium text-slate-700">{label}</span>
        <span className={`text-xs tabular-nums ${over ? 'text-red-600 font-semibold' : 'text-slate-500'}`}>
          {current.toFixed(0)} / {target.toFixed(0)} {unit}
        </span>
      </div>
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full ${over ? 'bg-red-500' : color} transition-all duration-300`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
