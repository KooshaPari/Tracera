import { Badge } from '@tracertm/ui/components/Badge'
import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { useState } from 'react'

type ReportFormat = 'json' | 'csv' | 'pdf' | 'xlsx'

interface ReportTemplate {
  id: string
  name: string
  description: string
  format: ReportFormat[]
  icon: string
}

const reportTemplates: ReportTemplate[] = [
  {
    id: 'coverage',
    name: 'Coverage Report',
    description: 'Requirements to features traceability',
    format: ['pdf', 'xlsx', 'csv'],
    icon: '📊',
  },
  {
    id: 'status',
    name: 'Status Report',
    description: 'Current project status overview',
    format: ['pdf', 'xlsx'],
    icon: '📈',
  },
  {
    id: 'items',
    name: 'Items Export',
    description: 'Export all items data',
    format: ['json', 'csv', 'xlsx'],
    icon: '📋',
  },
  {
    id: 'links',
    name: 'Links Export',
    description: 'Export all relationship links',
    format: ['json', 'csv'],
    icon: '🔗',
  },
]

export function ReportsView() {
  const [selectedFormat, setSelectedFormat] = useState<Record<string, ReportFormat>>({})

  const handleGenerate = (templateId: string) => {
    const format = selectedFormat[templateId] || 'pdf'
    console.log(`Generating ${templateId} report as ${format}`)
    // TODO: Implement actual report generation
    alert(`Generating ${templateId} report as ${format}`)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Reports</h1>
        <p className="text-gray-600">Generate and export reports</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reportTemplates.map((template) => (
          <Card key={template.id} className="p-6">
            <div className="flex items-start gap-4">
              <div className="text-4xl">{template.icon}</div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-1">{template.name}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {template.description}
                </p>

                <div className="flex items-center gap-2 mb-4">
                  <span className="text-sm text-gray-600">Format:</span>
                  {template.format.map((format) => (
                    <Badge
                      key={format}
                      variant={selectedFormat[template.id] === format ? 'default' : 'secondary'}
                      onClick={() =>
                        setSelectedFormat({ ...selectedFormat, [template.id]: format })
                      }
                      className="cursor-pointer"
                    >
                      {format.toUpperCase()}
                    </Badge>
                  ))}
                </div>

                <Button onClick={() => handleGenerate(template.id)} className="w-full">
                  Generate Report
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Reports</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <div className="font-medium">Coverage Report</div>
              <div className="text-sm text-gray-500">Generated 2 hours ago</div>
            </div>
            <Button variant="outline" size="sm">
              Download
            </Button>
          </div>
          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <div className="font-medium">Items Export</div>
              <div className="text-sm text-gray-500">Generated yesterday</div>
            </div>
            <Button variant="outline" size="sm">
              Download
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
