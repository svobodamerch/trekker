interface TextAreaProps {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  rows?: number
}

export function TextArea({ label, value, onChange, placeholder, rows = 3 }: TextAreaProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-soft-700">
        {label}
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        className="w-full px-4 py-3 rounded-xl border border-soft-200 bg-white text-soft-900 placeholder:text-soft-400 focus:outline-none focus:ring-2 focus:ring-soft-400 resize-none"
      />
    </div>
  )
}
