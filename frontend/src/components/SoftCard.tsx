import { ReactNode, MouseEvent } from 'react'

interface SoftCardProps {
  children: ReactNode
  className?: string
  onClick?: (e: MouseEvent<HTMLDivElement>) => void
}

export function SoftCard({ children, className = '', onClick }: SoftCardProps) {
  return (
    <div 
      onClick={onClick}
      className={`bg-white rounded-2xl border border-soft-100 shadow-sm ${className}`}
    >
      {children}
    </div>
  )
}
