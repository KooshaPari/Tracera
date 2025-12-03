import type { Meta, StoryObj } from '@storybook/react-vite'
import { Button, Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui'

const meta: Meta<typeof Card> = {
  title: 'Components/Card',
  component: Card,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Card content goes here. This is a sample card component.</p>
      </CardContent>
    </Card>
  ),
}

export const WithActions: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Project Card</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="mb-4 text-muted-foreground">A sample project with some description text.</p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Cancel
          </Button>
          <Button size="sm">Open</Button>
        </div>
      </CardContent>
    </Card>
  ),
}

export const Stats: Story = {
  render: () => (
    <div className="grid grid-cols-3 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Total Items</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">1,234</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">In Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold text-blue-500">42</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold text-green-500">892</p>
        </CardContent>
      </Card>
    </div>
  ),
}
