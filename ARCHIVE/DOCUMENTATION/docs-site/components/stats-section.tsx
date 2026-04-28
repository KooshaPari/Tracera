"use client"

import { motion, useInView, useMotionValue, useSpring } from "framer-motion"
import { useEffect, useRef } from "react"
import { Layout, Link2, Bot, FolderTree } from "lucide-react"

const stats = [
  {
    icon: Layout,
    value: 16,
    label: "Professional Views",
    suffix: "",
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-100 dark:bg-blue-950"
  },
  {
    icon: Link2,
    value: 60,
    label: "Link Types",
    suffix: "+",
    color: "text-purple-600 dark:text-purple-400",
    bgColor: "bg-purple-100 dark:bg-purple-950"
  },
  {
    icon: Bot,
    value: 1000,
    label: "Agents Supported",
    suffix: "+",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-950"
  },
  {
    icon: FolderTree,
    value: 12,
    label: "Link Categories",
    suffix: "",
    color: "text-yellow-600 dark:text-yellow-400",
    bgColor: "bg-yellow-100 dark:bg-yellow-950"
  }
]

function AnimatedCounter({ value, duration = 2 }: { value: number; duration?: number }) {
  const ref = useRef<HTMLSpanElement>(null)
  const motionValue = useMotionValue(0)
  const springValue = useSpring(motionValue, {
    damping: 60,
    stiffness: 100
  })
  const isInView = useInView(ref, { once: true, margin: "0px" })

  useEffect(() => {
    if (isInView) {
      motionValue.set(value)
    }
  }, [motionValue, isInView, value])

  useEffect(() => {
    springValue.on("change", (latest) => {
      if (ref.current) {
        ref.current.textContent = Intl.NumberFormat("en-US").format(Math.floor(latest))
      }
    })
  }, [springValue])

  return <span ref={ref} />
}

export function StatsSection() {
  return (
    <section className="py-20 bg-gradient-to-b from-gray-50 to-white dark:from-gray-950 dark:to-gray-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            By the Numbers
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Enterprise-grade requirements traceability with unprecedented scale and flexibility
          </p>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className={`w-16 h-16 rounded-2xl ${stat.bgColor} flex items-center justify-center mx-auto mb-4`}>
                  <Icon className={`w-8 h-8 ${stat.color}`} />
                </div>
                <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  <AnimatedCounter value={stat.value} />
                  {stat.suffix}
                </div>
                <div className="text-sm text-muted-foreground">
                  {stat.label}
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
