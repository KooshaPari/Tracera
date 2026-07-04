import type { ChangeEvent } from 'react';

import { useMutation } from '@tanstack/react-query';
import {
  Bell,
  Globe,
  Key,
  Link2,
  Monitor,
  RefreshCcw,
  Save,
  Settings as SettingsIcon,
  Shield,
  User,
} from 'lucide-react';
import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';

import { Checkbox } from '@/components/ui/checkbox';
import { useProjects } from '@/hooks/useProjects';
import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';
import { getProjectDisplayName } from '@/lib/project-name-utils';
import { cn } from '@/lib/utils';
import { Button } from '@tracertm/ui/components/Button';
import { Input } from '@tracertm/ui/components/Input';
import { Label } from '@tracertm/ui/components/Label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Separator } from '@tracertm/ui/components/Separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs';

import { saveSettings } from '../api/settings';

const IntegrationsView = lazy(async () =>
  import('@/pages/projects/views/IntegrationsView').then((m) => ({
    default: m.default ?? m.IntegrationsView,
  })),
);

type ThemeMode = 'light' | 'dark' | 'system';
type SaveSettingsPayload = Parameters<typeof saveSettings>[0];

interface SettingsTab {
  icon: typeof Bell;
  id: string;
  label: string;
}

interface PanelHeaderProps {
  subtitle: string;
  title: string;
}

interface NotificationToggleProps {
  checked: boolean;
  label: string;
  onChange: (checked: boolean) => void;
  subtitle: string;
}

interface ThemeOptionButtonProps {
  isActive: boolean;
  label: string;
  onSelect?: (label: string) => void;
}

const SETTINGS_TABS: SettingsTab[] = [
  { icon: User, id: 'profile', label: 'Identity' },
  { icon: Monitor, id: 'appearance', label: 'Visuals' },
  { icon: Key, id: 'api', label: 'Engine Access' },
  { icon: Bell, id: 'notifications', label: 'Comms' },
  { icon: Shield, id: 'security', label: 'Safety' },
  { icon: Link2, id: 'integrations', label: 'Integrations' },
];

const THEME_OPTIONS: ThemeMode[] = ['light', 'dark', 'system'];
const DENSITY_OPTIONS = ['low', 'medium', 'high'] as const;
const DEFAULT_TIMEZONE = 'UTC';
const DEFAULT_DENSITY = 'medium';

const PanelHeader = ({ subtitle, title }: PanelHeaderProps) => (
  <div className='space-y-1'>
    <h2 className='text-xl font-black tracking-tight uppercase'>{title}</h2>
    <p className='text-muted-foreground text-sm font-medium'>{subtitle}</p>
  </div>
);

const SettingsHeader = () => (
  <div className='mb-12 flex items-center gap-4'>
    <div className='bg-primary/10 flex h-14 w-14 items-center justify-center rounded-2xl'>
      <SettingsIcon className='text-primary h-7 w-7' />
    </div>
    <div>
      <h1 className='text-3xl font-black tracking-tight uppercase'>System Preferences</h1>
      <p className='text-muted-foreground text-[10px] font-medium tracking-widest uppercase'>
        Global Configuration Panel
      </p>
    </div>
  </div>
);

const SettingsSidebar = () => (
  <div className='space-y-4 lg:col-span-1'>
    <TabsList className='flex h-auto flex-col items-stretch space-y-1 bg-transparent'>
      {SETTINGS_TABS.map((tab) => (
        <TabsTrigger
          key={tab.id}
          value={tab.id}
          className='data-[state=active]:bg-primary data-[state=active]:text-primary-foreground hover:border-border justify-start gap-3 rounded-xl border border-transparent px-4 py-3 transition-all'
        >
          <tab.icon className='h-4 w-4' />
          <span className='text-sm font-bold tracking-tight'>{tab.label}</span>
        </TabsTrigger>
      ))}
    </TabsList>
  </div>
);

const ThemeOptionButton = ({ isActive, label, onSelect }: ThemeOptionButtonProps) => {
  const handleClick = useCallback(() => {
    if (onSelect) {
      onSelect(label);
    }
  }, [label, onSelect]);

  return (
    <button
      onClick={onSelect ? handleClick : undefined}
      className={cn(
        'px-4 py-2 rounded-xl text-[10px] font-black uppercase border transition-all',
        isActive
          ? 'bg-primary text-primary-foreground border-primary'
          : 'bg-background border-border hover:border-primary/50',
      )}
      type='button'
    >
      {label}
    </button>
  );
};

const NotificationToggle = ({ checked, label, onChange, subtitle }: NotificationToggleProps) => (
  <div className='bg-muted/30 hover:bg-muted/50 flex items-center justify-between rounded-2xl p-5 transition-colors'>
    <div className='space-y-1'>
      <p className='text-sm font-bold tracking-tight uppercase'>{label}</p>
      <p className='text-muted-foreground text-[10px] font-medium uppercase'>{subtitle}</p>
    </div>
    <Checkbox
      checked={checked}
      onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
        onChange(e.target.checked);
      }}
      className='h-6 w-6 rounded-lg border-2'
    />
  </div>
);

interface ProfilePanelProps {
  displayName: string;
  email: string;
  onDisplayNameChange: (nextValue: string) => void;
  onEmailChange: (nextValue: string) => void;
}

const ProfilePanel = ({
  displayName,
  email,
  onDisplayNameChange,
  onEmailChange,
}: ProfilePanelProps) => {
  const handleDisplayNameChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onDisplayNameChange(event.target.value);
    },
    [onDisplayNameChange],
  );

  const handleEmailChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onEmailChange(event.target.value);
    },
    [onEmailChange],
  );

  return (
    <TabsContent
      value='profile'
      className='animate-in slide-in-from-right-2 mt-0 space-y-8 duration-300'
    >
      <PanelHeader title='Public Identity' subtitle='How you appear across the project network.' />
      <Separator className='bg-border/50' />
      <div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
        <div className='space-y-2'>
          <Label className='text-muted-foreground ml-1 text-[10px] font-black tracking-widest uppercase'>
            Registry Name
          </Label>
          <Input
            value={displayName}
            onChange={handleDisplayNameChange}
            className='bg-muted/30 h-12 rounded-xl border-none font-bold'
          />
        </div>
        <div className='space-y-2'>
          <Label className='text-muted-foreground ml-1 text-[10px] font-black tracking-widest uppercase'>
            Direct Comms (Email)
          </Label>
          <Input
            type='email'
            value={email}
            onChange={handleEmailChange}
            className='bg-muted/30 h-12 rounded-xl border-none font-bold'
          />
        </div>
      </div>
      <div className='space-y-2 pt-4'>
        <Label className='text-muted-foreground ml-1 text-[10px] font-black tracking-widest uppercase'>
          Timezone / Location Context
        </Label>
        <Select value={DEFAULT_TIMEZONE}>
          <SelectTrigger className='bg-muted/30 h-12 rounded-xl border-none font-bold'>
            <div className='flex items-center gap-2'>
              <Globe className='text-primary h-4 w-4' />
              <SelectValue />
            </div>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='UTC' className='font-bold'>
              Coordinated Universal Time (UTC)
            </SelectItem>
            <SelectItem value='PST' className='font-bold'>
              Pacific Standard Time
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
    </TabsContent>
  );
};

interface AppearancePanelProps {
  onThemeChange: (theme: ThemeMode) => void;
  theme: ThemeMode;
}

const AppearancePanel = ({ onThemeChange, theme }: AppearancePanelProps) => {
  const handleThemeSelect = useCallback(
    (nextTheme: string) => {
      onThemeChange(nextTheme as ThemeMode);
    },
    [onThemeChange],
  );

  return (
    <TabsContent
      value='appearance'
      className='animate-in slide-in-from-right-2 mt-0 space-y-8 duration-300'
    >
      <PanelHeader
        title='Interface Directives'
        subtitle='Configure visual rendering and layouts.'
      />
      <Separator className='bg-border/50' />
      <div className='space-y-6'>
        <div className='bg-muted/30 flex items-center justify-between rounded-2xl p-4'>
          <div className='space-y-1'>
            <p className='text-sm font-bold tracking-tight uppercase'>Color Schema</p>
            <p className='text-muted-foreground text-[10px] font-medium uppercase'>
              Adaptive, dark or light mode
            </p>
          </div>
          <div className='flex gap-1'>
            {THEME_OPTIONS.map((option) => (
              <ThemeOptionButton
                key={option}
                label={option}
                isActive={theme === option}
                onSelect={handleThemeSelect}
              />
            ))}
          </div>
        </div>

        <div className='bg-muted/30 flex items-center justify-between rounded-2xl p-4'>
          <div className='space-y-1'>
            <p className='text-sm font-bold tracking-tight uppercase'>Information Density</p>
            <p className='text-muted-foreground text-[10px] font-medium uppercase'>
              Scaling for data presentation
            </p>
          </div>
          <div className='flex gap-1'>
            {DENSITY_OPTIONS.map((density) => (
              <ThemeOptionButton
                key={density}
                label={density}
                isActive={density === DEFAULT_DENSITY}
              />
            ))}
          </div>
        </div>
      </div>
    </TabsContent>
  );
};

const ApiPanel = () => (
  <TabsContent value='api' className='animate-in slide-in-from-right-2 mt-0 space-y-8 duration-300'>
    <PanelHeader
      title='Engine Interface Access'
      subtitle='Manage cryptographic keys for external integrations.'
    />
    <Separator className='bg-border/50' />
    <div className='space-y-6'>
      <div className='bg-muted/10 space-y-4 rounded-2xl border-2 border-dashed p-6'>
        <div className='space-y-2'>
          <Label className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            Master API Link
          </Label>
          <div className='flex gap-2'>
            <Input
              type='password'
              value='************************'
              disabled
              className='bg-background h-12 rounded-xl border-none font-mono shadow-sm'
            />
            <Button
              variant='outline'
              className='h-12 rounded-xl px-6 text-[10px] font-black tracking-widest uppercase'
            >
              REGEN
            </Button>
          </div>
        </div>
        <p className='text-muted-foreground text-[10px] leading-relaxed font-medium italic'>
          Caution: API keys grant deep access to the graph repository. Never expose these in
          client-side codebases.
        </p>
      </div>
    </div>
  </TabsContent>
);

interface NotificationsPanelProps {
  desktopNotifications: boolean;
  emailNotifications: boolean;
  onDesktopNotificationsChange: (checked: boolean) => void;
  onEmailNotificationsChange: (checked: boolean) => void;
  onWeeklySummaryChange: (checked: boolean) => void;
  weeklySummary: boolean;
  // Type annotations explicitly define checked parameter as boolean
}

const NotificationsPanel = ({
  desktopNotifications,
  emailNotifications,
  onDesktopNotificationsChange,
  onEmailNotificationsChange,
  onWeeklySummaryChange,
  weeklySummary,
}: NotificationsPanelProps) => (
  <TabsContent
    value='notifications'
    className='animate-in slide-in-from-right-2 mt-0 space-y-8 duration-300'
  >
    <PanelHeader
      title='Telemetry & Comms'
      subtitle='Control notification frequency and channels.'
    />
    <Separator className='bg-border/50' />
    <div className='space-y-4'>
      <NotificationToggle
        checked={emailNotifications}
        label='Email Dispatches'
        subtitle='System status and daily digests'
        onChange={onEmailNotificationsChange}
      />
      <NotificationToggle
        checked={desktopNotifications}
        label='Desktop Stream'
        subtitle='Real-time push alerts for link changes'
        onChange={onDesktopNotificationsChange}
      />
      <NotificationToggle
        checked={weeklySummary}
        label='Executive Weekly'
        subtitle='Intelligence summary of project health'
        onChange={onWeeklySummaryChange}
      />
    </div>
  </TabsContent>
);

interface IntegrationsPanelProps {
  integrationProjectId: string;
  projects: ReturnType<typeof useProjects>['data'];
  onProjectChange: (projectId: string) => void;
}

const IntegrationsPanel = ({
  integrationProjectId,
  onProjectChange,
  projects,
}: IntegrationsPanelProps) => (
  <TabsContent
    value='integrations'
    className='animate-in slide-in-from-right-2 mt-0 space-y-8 duration-300'
  >
    <PanelHeader
      title='Account Integrations'
      subtitle='Link external accounts once, then map them per project.'
    />
    <Separator className='bg-border/50' />
    <div className='space-y-4'>
      <div className='space-y-2'>
        <Label className='text-muted-foreground ml-1 text-[10px] font-black tracking-widest uppercase'>
          Project Context
        </Label>
        <Select value={integrationProjectId || 'none'} onValueChange={onProjectChange}>
          <SelectTrigger className='bg-muted/30 h-12 rounded-xl border-none font-bold'>
            <SelectValue placeholder='Select a project to link accounts' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='none' className='font-bold'>
              No project selected
            </SelectItem>
            {Array.isArray(projects) &&
              projects.map((project) => (
                <SelectItem key={project.id} value={project.id} className='font-bold'>
                  {getProjectDisplayName(project)}
                </SelectItem>
              ))}
          </SelectContent>
        </Select>
      </div>

      {integrationProjectId ? (
        <Suspense fallback={<ChunkLoadingSkeleton message='Loading integrations...' />}>
          <IntegrationsView projectId={integrationProjectId} mode='account' initialTab='overview' />
        </Suspense>
      ) : (
        <div className='text-muted-foreground text-sm'>
          Select a project to link external accounts.
        </div>
      )}
    </div>
  </TabsContent>
);

interface SettingsFooterProps {
  isSaving: boolean;
  onSave: () => void;
}

const SettingsFooter = ({ isSaving, onSave }: SettingsFooterProps) => (
  <div className='bg-background/80 fixed right-0 bottom-0 left-0 z-50 border-t p-6 backdrop-blur-md lg:left-72'>
    <div className='mx-auto flex max-w-5xl justify-end gap-4'>
      <Button
        variant='ghost'
        className='rounded-xl px-8 text-[10px] font-black tracking-[0.2em] uppercase'
      >
        Reset Panel
      </Button>
      <Button
        onClick={onSave}
        disabled={isSaving}
        className='shadow-primary/20 h-12 gap-3 rounded-xl px-12 text-[10px] font-black tracking-[0.2em] uppercase shadow-xl'
      >
        {isSaving ? <RefreshCcw className='h-4 w-4 animate-spin' /> : <Save className='h-4 w-4' />}
        Synchronize Parameters
      </Button>
    </div>
  </div>
);

export const SettingsView = () => {
  const [theme, setTheme] = useState<ThemeMode>('system');
  const [displayName, setDisplayName] = useState('System Administrator');
  const [email, setEmail] = useState('admin@tracertm.io');
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [desktopNotifications, setDesktopNotifications] = useState(false);
  const [weeklySummary, setWeeklySummary] = useState(true);
  const { data: projects } = useProjects();
  const [integrationProjectId, setIntegrationProjectId] = useState<string>('');

  useEffect(() => {
    if (!integrationProjectId && Array.isArray(projects) && projects.length > 0 && projects[0]) {
      setIntegrationProjectId(projects[0].id);
    }
  }, [integrationProjectId, projects]);

  const saveSettingsMutation = useMutation({
    mutationFn: async (settings: SaveSettingsPayload) => saveSettings(settings),
    onError: (error: Error) => {
      toast.error(`Sync failure: ${error.message}`);
    },
    onSuccess: () => {
      toast.success('Identity parameters synchronized');
    },
  });

  const handleSave = useCallback(() => {
    saveSettingsMutation.mutate({
      desktopNotifications,
      displayName,
      email,
      emailNotifications,
      theme,
      weeklySummary,
    });
  }, [
    desktopNotifications,
    displayName,
    email,
    emailNotifications,
    saveSettingsMutation,
    theme,
    weeklySummary,
  ]);

  const handleDisplayNameChange = useCallback((nextValue: string) => {
    setDisplayName(nextValue);
  }, []);

  const handleEmailChange = useCallback((nextValue: string) => {
    setEmail(nextValue);
  }, []);

  const handleThemeChange = useCallback((nextTheme: ThemeMode) => {
    setTheme(nextTheme);
  }, []);

  const handleEmailNotificationsChange = useCallback((checked: boolean) => {
    setEmailNotifications(checked);
  }, []);

  const handleDesktopNotificationsChange = useCallback((checked: boolean) => {
    setDesktopNotifications(checked);
  }, []);

  const handleWeeklySummaryChange = useCallback((checked: boolean) => {
    setWeeklySummary(checked);
  }, []);

  const handleProjectChange = useCallback((value: string) => {
    setIntegrationProjectId(value === 'none' ? '' : value);
  }, []);

  const tabsClassName = useMemo(() => 'grid grid-cols-1 lg:grid-cols-4 gap-12 items-start', []);

  return (
    <div className='animate-in-fade-up mx-auto max-w-5xl space-y-8 p-6 pb-24'>
      <SettingsHeader />
      <Tabs defaultValue='profile' className={tabsClassName}>
        <SettingsSidebar />
        <div className='lg:col-span-3'>
          <ProfilePanel
            displayName={displayName}
            email={email}
            onDisplayNameChange={handleDisplayNameChange}
            onEmailChange={handleEmailChange}
          />
          <AppearancePanel theme={theme} onThemeChange={handleThemeChange} />
          <ApiPanel />
          <NotificationsPanel
            emailNotifications={emailNotifications}
            desktopNotifications={desktopNotifications}
            weeklySummary={weeklySummary}
            onEmailNotificationsChange={handleEmailNotificationsChange}
            onDesktopNotificationsChange={handleDesktopNotificationsChange}
            onWeeklySummaryChange={handleWeeklySummaryChange}
          />
          <IntegrationsPanel
            integrationProjectId={integrationProjectId}
            projects={projects}
            onProjectChange={handleProjectChange}
          />
          <SettingsFooter isSaving={saveSettingsMutation.isPending} onSave={handleSave} />
        </div>
      </Tabs>
    </div>
  );
};
