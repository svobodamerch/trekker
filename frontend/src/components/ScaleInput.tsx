interface ScaleInputProps {
  label: string
  value: number | null | undefined
  onChange: (value: number) => void
  min?: number
  max?: number
}

export function ScaleInput({ label, value, onChange, min = 1, max = 10 }: ScaleInputProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-soft-700">
        {label}
      </label>
      <div className="flex gap-2">
        {Array.from({ length: max - min + 1 }, (_, i) => i + min).map((num) => (
          <button
            key={num}
            type="button"
            onClick={() => onChange(num)}
            className={`w-10 h-10 rounded-lg text-sm font-medium transition-colors ${
              value === num
                ? 'bg-soft-600 text-white'
                : 'bg-white border border-soft-200 text-soft-600 hover:border-soft-400'
            }`}
          >
            {num}
          </button>
        ))}
      </div>
    </div>
  )
}
