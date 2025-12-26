'use client'
import React, { useRef, useState, useCallback, useEffect } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'
import { cn } from '@/lib/utils'

export function SpotlightHover({ className, size = 200 }) {
  const ref = useRef<HTMLDivElement>(null)
  const mouseX = useSpring(0)
  const mouseY = useSpring(0)

  const left = useTransform(mouseX, x => `${x - size / 2}px`)
  const top = useTransform(mouseY, y => `${y - size / 2}px`)

  const move = useCallback((e: MouseEvent) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    mouseX.set(e.clientX - rect.left)
    mouseY.set(e.clientY - rect.top)
  }, [])

  useEffect(() => {
    window.addEventListener('mousemove', move)
    return () => window.removeEventListener('mousemove', move)
  }, [move])

  return (
    <motion.div
      ref={ref}
      className={cn(
        "pointer-events-none absolute rounded-full blur-xl bg-white/20",
        className
      )}
      style={{ width: size, height: size, left, top }}
    />
  )
}
