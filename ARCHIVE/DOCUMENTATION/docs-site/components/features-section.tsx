"use client"

import { motion } from "framer-motion"
import {
  Layout,
  Link2,
  Bot,
  History,
  Layers,
  Users,
  Database,
  Workflow
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card"

const features = [
  {
    icon: Layout,
    title: "16 Professional Views",
    description: "Feature, Code, Test, API, Wireframe, Database, Architecture, and 9 more specialized views for comprehensive project visibility.",
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-100 dark:bg-blue-950"
  },
  {
    icon: Link2,
    title: "60+ Link Types",
    description: "Rich relationship modeling across Hierarchical, Dependency, Implementation, Testing, and 8 more categories.",
    color: "text-purple-600 dark:text-purple-400",
    bgColor: "bg-purple-100 dark:bg-purple-950"
  },
  {
    icon: Bot,
    title: "Agent-Native Architecture",
    description: "Support for 1-1000 concurrent autonomous agents with NATS messaging and real-time coordination.",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-950"
  },
  {
    icon: History,
    title: "Event Sourcing",
    description: "Complete audit trail and time-travel capabilities for compliance and debugging with full history preservation.",
    color: "text-orange-600 dark:text-orange-400",
    bgColor: "bg-orange-100 dark:bg-orange-950"
  },
  {
    icon: Layers,
    title: "Multi-Platform",
    description: "CLI (Python), REST API (Go), Web UI (React), and Desktop (Tauri) applications for maximum flexibility.",
    color: "text-pink-600 dark:text-pink-400",
    bgColor: "bg-pink-100 dark:bg-pink-950"
  },
  {
    icon: Users,
    title: "Real-Time Collaboration",
    description: "WebSocket-based live updates across all clients with conflict resolution and presence awareness.",
    color: "text-cyan-600 dark:text-cyan-400",
    bgColor: "bg-cyan-100 dark:bg-cyan-950"
  },
  {
    icon: Database,
    title: "Graph Database",
    description: "Neo4j integration for complex relationship queries with PostgreSQL for relational data storage.",
    color: "text-indigo-600 dark:text-indigo-400",
    bgColor: "bg-indigo-100 dark:bg-indigo-950"
  },
  {
    icon: Workflow,
    title: "Intelligent CRUD",
    description: "Auto-generation, smart extension, and intelligent collapse operations for efficient requirements management.",
    color: "text-yellow-600 dark:text-yellow-400",
    bgColor: "bg-yellow-100 dark:bg-yellow-950"
  }
]

export function FeaturesSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5
      }
    }
  }

  return (
    <section className="py-20 bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-950">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Powerful Features
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need for comprehensive requirements traceability management
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div key={index} variants={itemVariants}>
                <Card className="h-full border-2 hover:border-primary/50 transition-colors duration-300 hover:shadow-lg group">
                  <CardHeader>
                    <div className={`w-12 h-12 rounded-lg ${feature.bgColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className={`w-6 h-6 ${feature.color}`} />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm">
                      {feature.description}
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
