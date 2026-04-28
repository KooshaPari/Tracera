'use client'

import React, { useState } from 'react'

/**
 * Simple Tabs component
 */
function Tabs({ defaultValue, children, className }: { defaultValue: string; children: React.ReactNode; className?: string }) {
  const [activeTab, setActiveTab] = useState(defaultValue)
  return (
    <div className={className}>
      {React.Children.map(children, (child) =>
        React.isValidElement(child)
          ? React.cloneElement(child as React.ReactElement<any>, { activeTab, setActiveTab })
          : child
      )}
    </div>
  )
}

function TabsList({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={`flex border-b ${className || ''}`}>{children}</div>
}

function TabsTrigger({
  value,
  children,
  activeTab,
  setActiveTab,
}: {
  value: string
  children: React.ReactNode
  activeTab?: string
  setActiveTab?: (v: string) => void
}) {
  return (
    <button
      onClick={() => setActiveTab?.(value)}
      className={`px-4 py-2 font-medium transition-colors ${
        activeTab === value
          ? 'border-b-2 border-primary text-primary'
          : 'text-foreground/60 hover:text-foreground'
      }`}
    >
      {children}
    </button>
  )
}

function TabsContent({
  value,
  children,
  activeTab,
}: {
  value: string
  children: React.ReactNode
  activeTab?: string
}) {
  return activeTab === value ? <div className="space-y-4 py-4">{children}</div> : null
}

/**
 * CLIFrontendComparison - Switch between CLI and Frontend demos
 */
export function CLIFrontendComparison({
  cliDemo,
  frontendDemo,
  cliLabel = 'CLI',
  frontendLabel = 'Frontend',
}: {
  cliDemo: React.ReactNode
  frontendDemo: React.ReactNode
  cliLabel?: string
  frontendLabel?: string
}) {
  const [activeTab, setActiveTab] = useState('cli')
  return (
    <div className="w-full my-6 border rounded-lg overflow-hidden">
      <div className="flex border-b bg-muted">
        <button
          onClick={() => setActiveTab('cli')}
          className={`flex-1 px-4 py-3 font-medium transition-colors ${
            activeTab === 'cli'
              ? 'bg-background text-foreground border-b-2 border-primary'
              : 'text-foreground/60 hover:text-foreground'
          }`}
        >
          💻 {cliLabel}
        </button>
        <button
          onClick={() => setActiveTab('frontend')}
          className={`flex-1 px-4 py-3 font-medium transition-colors ${
            activeTab === 'frontend'
              ? 'bg-background text-foreground border-b-2 border-primary'
              : 'text-foreground/60 hover:text-foreground'
          }`}
        >
          🎨 {frontendLabel}
        </button>
      </div>
      <div className="p-4">
        {activeTab === 'cli' && <div className="space-y-4">{cliDemo}</div>}
        {activeTab === 'frontend' && <div className="space-y-4">{frontendDemo}</div>}
      </div>
    </div>
  )
}

/**
 * DemoPlayer - Display GIF with caption and description
 */
export function DemoPlayer({
  src,
  alt,
  caption,
  description,
}: {
  src: string
  alt: string
  caption: string
  description?: string
}) {
  return (
    <figure className="my-6 border rounded-lg overflow-hidden bg-muted p-4">
      <div className="bg-black rounded aspect-video flex items-center justify-center mb-4">
        <img
          src={src}
          alt={alt}
          className="max-w-full max-h-full"
        />
      </div>
      <figcaption className="text-sm font-semibold text-foreground mb-2">
        {caption}
      </figcaption>
      {description && (
        <p className="text-sm text-foreground/80">{description}</p>
      )}
    </figure>
  )
}

/**
 * CodeComparison - Side-by-side code examples
 */
export function CodeComparison({
  language1,
  code1,
  label1,
  language2,
  code2,
  label2,
}: {
  language1: string
  code1: string
  label1: string
  language2: string
  code2: string
  label2: string
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-muted px-4 py-2 font-semibold text-sm">{label1}</div>
        <pre className="p-4 overflow-x-auto text-sm">
          <code className={`language-${language1}`}>{code1}</code>
        </pre>
      </div>
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-muted px-4 py-2 font-semibold text-sm">{label2}</div>
        <pre className="p-4 overflow-x-auto text-sm">
          <code className={`language-${language2}`}>{code2}</code>
        </pre>
      </div>
    </div>
  )
}

/**
 * FeatureGrid - Display features in a grid with icons
 */
export function FeatureGrid({
  features,
}: {
  features: Array<{
    icon: string
    title: string
    description: string
  }>
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 my-6">
      {features.map((feature, idx) => (
        <div key={idx} className="border rounded-lg p-4 hover:bg-muted/50 transition">
          <div className="text-3xl mb-2">{feature.icon}</div>
          <h3 className="font-semibold mb-2">{feature.title}</h3>
          <p className="text-sm text-foreground/80">{feature.description}</p>
        </div>
      ))}
    </div>
  )
}

/**
 * WorkflowSteps - Display workflow with numbered steps
 */
export function WorkflowSteps({
  steps,
}: {
  steps: Array<{
    number: number
    title: string
    description: string
    code?: string
    language?: string
  }>
}) {
  return (
    <div className="space-y-6 my-6">
      {steps.map((step) => (
        <div key={step.number} className="flex gap-4">
          <div className="flex-shrink-0">
            <div className="flex items-center justify-center h-10 w-10 rounded-full bg-primary text-primary-foreground font-semibold">
              {step.number}
            </div>
          </div>
          <div className="flex-grow">
            <h3 className="font-semibold mb-2">{step.title}</h3>
            <p className="text-sm text-foreground/80 mb-3">{step.description}</p>
            {step.code && (
              <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
                <code className={`language-${step.language || 'bash'}`}>
                  {step.code}
                </code>
              </pre>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

