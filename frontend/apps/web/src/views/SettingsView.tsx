import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Input } from '@tracertm/ui/components/Input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@tracertm/ui/components/Select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs'
import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'

export function SettingsView() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system')
  const [apiKey, setApiKey] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [fontSize, setFontSize] = useState('medium')
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [desktopNotifications, setDesktopNotifications] = useState(false)
  const [weeklySummary, setWeeklySummary] = useState(true)

  const saveSettingsMutation = useMutation({
    mutationFn: async (settings: any) => {
      // TODO: Implement API call to save settings
      return Promise.resolve(settings)
    },
    onSuccess: () => {
      alert('Settings saved successfully!')
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-gray-600">Manage your preferences and configuration</p>
      </div>

      <Card className="p-6">
        <Tabs defaultValue="general">
          <TabsList>
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
            <TabsTrigger value="api">API Keys</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
          </TabsList>

          <TabsContent value="general">
            <div className="space-y-6 mt-6">
              <div>
                <label htmlFor="display-name" className="block text-sm font-medium mb-2">
                  Display Name
                </label>
                <Input
                  id="display-name"
                  placeholder="Your name"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="mt-2"
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-2">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-2"
                />
              </div>
              <div>
                <label htmlFor="timezone" className="block text-sm font-medium mb-2">
                  Timezone
                </label>
                <Select value="UTC" onValueChange={() => {}}>
                  <SelectTrigger id="timezone" className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="UTC">UTC</SelectItem>
                    <SelectItem value="America/New_York">Eastern Time</SelectItem>
                    <SelectItem value="America/Chicago">Central Time</SelectItem>
                    <SelectItem value="America/Denver">Mountain Time</SelectItem>
                    <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() =>
                  saveSettingsMutation.mutate({
                    displayName,
                    email,
                    theme,
                    fontSize,
                  })
                }
                disabled={saveSettingsMutation.isPending}
              >
                {saveSettingsMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="appearance">
            <div className="space-y-6 mt-6">
              <div>
                <label htmlFor="theme-select" className="block text-sm font-medium mb-2">
                  Theme
                </label>
                <Select value={theme} onValueChange={(v) => setTheme(v as typeof theme)}>
                  <SelectTrigger id="theme-select" className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label htmlFor="font-size-select" className="block text-sm font-medium mb-2">
                  Font Size
                </label>
                <Select value={fontSize} onValueChange={setFontSize}>
                  <SelectTrigger id="font-size-select" className="mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="small">Small</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="large">Large</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label htmlFor="compact-mode" className="block text-sm font-medium mb-2">
                  Compact Mode
                </label>
                <div className="flex items-center gap-2 mt-2">
                  <input type="checkbox" id="compact-mode" className="w-5 h-5" />
                  <span className="text-sm text-gray-600">Use compact layout</span>
                </div>
              </div>
              <Button
                onClick={() =>
                  saveSettingsMutation.mutate({
                    theme,
                    fontSize,
                  })
                }
                disabled={saveSettingsMutation.isPending}
              >
                {saveSettingsMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="api">
            <div className="space-y-6 mt-6">
              <div>
                <label htmlFor="api-key" className="block text-sm font-medium mb-2">
                  API Key
                </label>
                <Input
                  id="api-key"
                  type="password"
                  value={apiKey}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setApiKey((e.currentTarget as HTMLInputElement).value)
                  }
                  placeholder="Enter API key"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Used for external integrations and webhooks
                </p>
              </div>
              <div className="flex gap-2">
                <Button>Generate New Key</Button>
                <Button variant="outline">Revoke Key</Button>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="notifications">
            <div className="space-y-6 mt-6">
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="email-notifications" className="block font-medium">
                    Email Notifications
                  </label>
                  <div className="text-sm text-gray-500">Receive email updates</div>
                </div>
                <input
                  type="checkbox"
                  id="email-notifications"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                  className="w-5 h-5"
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="desktop-notifications" className="block font-medium">
                    Desktop Notifications
                  </label>
                  <div className="text-sm text-gray-500">Browser push notifications</div>
                </div>
                <input
                  type="checkbox"
                  id="desktop-notifications"
                  checked={desktopNotifications}
                  onChange={(e) => setDesktopNotifications(e.target.checked)}
                  className="w-5 h-5"
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="weekly-summary" className="block font-medium">
                    Weekly Summary
                  </label>
                  <div className="text-sm text-gray-500">Get a weekly digest</div>
                </div>
                <input
                  type="checkbox"
                  id="weekly-summary"
                  checked={weeklySummary}
                  onChange={(e) => setWeeklySummary(e.target.checked)}
                  className="w-5 h-5"
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="item-updates" className="block font-medium">
                    Item Updates
                  </label>
                  <div className="text-sm text-gray-500">Notify when items change</div>
                </div>
                <input type="checkbox" id="item-updates" className="w-5 h-5" />
              </div>
              <Button
                onClick={() =>
                  saveSettingsMutation.mutate({
                    emailNotifications,
                    desktopNotifications,
                    weeklySummary,
                  })
                }
                disabled={saveSettingsMutation.isPending}
              >
                {saveSettingsMutation.isPending ? 'Saving...' : 'Save Preferences'}
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}
