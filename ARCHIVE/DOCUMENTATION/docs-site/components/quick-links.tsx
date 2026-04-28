"use client"

import { motion } from "framer-motion"
import {
  Zap,
  Network,
  LayoutGrid,
  Terminal,
  FileCheck,
  ArrowRight
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card"
import { Button } from "./button"

const links = [
  {
    icon: Zap,
    title: "5-Minute Quick Start",
    description: "Install TraceRTM and create your first traceability matrix",
    href: "/docs/getting-started/quick-start",
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-50 dark:bg-blue-950/50"
  },
  {
    icon: LayoutGrid,
    title: "16 Artifact Views",
    description: "Understand Requirements, Features, Tests, and other traceability artifacts",
    href: "/docs/wiki/concepts/artifacts",
    color: "text-purple-600 dark:text-purple-400",
    bgColor: "bg-purple-50 dark:bg-purple-950/50"
  },
  {
    icon: Network,
    title: "Link Types & Relationships",
    description: "Learn how to create bidirectional traceability between artifacts",
    href: "/docs/wiki/concepts/relationships",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-50 dark:bg-green-950/50"
  },
  {
    icon: FileCheck,
    title: "Feature Workflow Example",
    description: "Follow a complete example from requirement to implementation",
    href: "/docs/wiki/examples/basic-workflow",
    color: "text-orange-600 dark:text-orange-400",
    bgColor: "bg-orange-50 dark:bg-orange-950/50"
  },
  {
    icon: Terminal,
    title: "CLI Commands",
    description: "Complete reference for TraceRTM command-line interface",
    href: "/docs/api-reference/cli",
    color: "text-pink-600 dark:text-pink-400",
    bgColor: "bg-pink-50 dark:bg-pink-950/50"
  }
]

export function QuickLinks() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.5
      }
    }
  }

  return (
    <section className="py-20 bg-white dark:bg-gray-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Quick Links
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Jump right into what you need
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto"
        >
          {links.map((link, index) => {
            const Icon = link.icon
            return (
              <motion.div key={index} variants={itemVariants}>
                <Card className={`h-full ${link.bgColor} border-2 hover:border-primary/50 transition-all duration-300 hover:shadow-lg group cursor-pointer`}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <Icon className={`w-6 h-6 ${link.color}`} />
                        <CardTitle className="text-lg">{link.title}</CardTitle>
                      </div>
                      <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:translate-x-1 transition-transform duration-300" />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm">
                      {link.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}
