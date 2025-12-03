import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Input } from '@tracertm/ui/components/Input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs'
import { useState } from 'react'

export function SettingsView() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system')
  const [apiKey, setApiKey] = useState('')

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
                <label className="block text-sm font-medium mb-2">Display Name</label>
                <Input placeholder="Your name" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <Input type="email" placeholder="your@email.com" />
              </div>
              <Button>Save Changes</Button>
            </div>
          </TabsContent>

          <TabsContent value="appearance">
            <div className="space-y-6 mt-6">
              <div>
                <label className="block text-sm font-medium mb-2">Theme</label>
                <div className="flex gap-4">
                  {(['light', 'dark', 'system'] as const).map((t) => (
                    <button
                      key={t}
                      onClick={() => setTheme(t)}
                      className={`px-4 py-2 border rounded-lg ${theme === t ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : ''}`}
                    >
                      {t.charAt(0).toUpperCase() + t.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Font Size</label>
                <select className="px-3 py-2 border rounded-md w-full">
                  <option>Small</option>
                  <option>Medium</option>
                  <option>Large</option>
                </select>
              </div>
              <Button>Save Changes</Button>
            </div>
          </TabsContent>

          <TabsContent value="api">
            <div className="space-y-6 mt-6">
              <div>
                <label className="block text-sm font-medium mb-2">API Key</label>
                <Input
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
                  <div className="font-medium">Email Notifications</div>
                  <div className="text-sm text-gray-500">Receive email updates</div>
                </div>
                <input type="checkbox" className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Desktop Notifications</div>
                  <div className="text-sm text-gray-500">Browser push notifications</div>
                </div>
                <input type="checkbox" className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Weekly Summary</div>
                  <div className="text-sm text-gray-500">Get a weekly digest</div>
                </div>
                <input type="checkbox" className="w-5 h-5" />
              </div>
              <Button>Save Preferences</Button>
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}
