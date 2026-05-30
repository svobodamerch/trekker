interface SliderInputProps {
  label: string
  value: number | undefined
  onChange: (value: number) => void
  min?: number
  max?: number
  leftLabel?: string
  rightLabel?: string
}

export function SliderInput({
  label,
  value,
  onChange,
  min = 0,
  max = 10,
  leftLabel = 'Низкое',
  rightLabel = 'Высокое',
}: SliderInputProps) {
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-soft-700">{label}</label>
        <span className="text-lg font-semibold text-soft-800 w-8 text-center">
          {value ?? '-'}
        </span>
      </div>

      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          value={value ?? min}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 bg-soft-200 rounded-lg appearance-none cursor-pointer accent-soft-600 hover:accent-soft-700"
        />
        <div className="flex justify-between text-xs text-soft-400 mt-1">
          <span>{min}</span>
          <span>{max}</span>
        </div>
      </div>

      <div className="flex justify-between text-xs text-soft-500">
        <span>{leftLabel}</span>
        <span>{rightLabel}</span>
      </div>
    </div>
  )
}
