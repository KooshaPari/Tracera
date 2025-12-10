"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, Github, FileText, Zap } from "lucide-react"
import { Button } from "./button"
import { Badge } from "./badge"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-32">
      {/* Animated Background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-blue-950 dark:via-gray-900 dark:to-purple-950" />
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-400/20 dark:bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-400/20 dark:bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-700" />
        </div>
        
        {/* Grid Pattern */}
        <div className="absolute inset-0 bg-grid-slate-100 dark:bg-grid-slate-800/[0.4] bg-[size:60px_60px]" />
      </div>

      <div className="container relative mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center space-y-8">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Badge variant="secondary" className="px-4 py-1.5 text-sm">
              <Zap className="w-3 h-3 mr-1.5 inline" />
              Version 1.0.0 - Now Available
            </Badge>
          </motion.div>

          {/* Main Heading */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="space-y-4"
          >
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
              TraceRTM
            </h1>
            <p className="text-xl sm:text-2xl lg:text-3xl font-semibold text-gray-900 dark:text-gray-100">
              Multi-View Requirements Traceability
            </p>
          </motion.div>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="max-w-2xl text-lg sm:text-xl text-muted-foreground"
          >
            A hybrid, agent-native requirements traceability and project management system with 16 professional views, 60+ link types, and intelligent CRUD operations.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <Link href="/docs/getting-started">
              <Button size="lg" className="group">
                <FileText className="mr-2 h-5 w-5" />
                Get Started
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/docs/api-reference">
              <Button size="lg" variant="outline">
                <FileText className="mr-2 h-5 w-5" />
                API Documentation
              </Button>
            </Link>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">
              <Button size="lg" variant="outline">
                <Github className="mr-2 h-5 w-5" />
                View on GitHub
              </Button>
            </a>
          </motion.div>

          {/* Stats Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="grid grid-cols-3 gap-8 pt-8"
          >
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">16</div>
              <div className="text-sm text-muted-foreground">Views</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">60+</div>
              <div className="text-sm text-muted-foreground">Link Types</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400">1000+</div>
              <div className="text-sm text-muted-foreground">Agents</div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
