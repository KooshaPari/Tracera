import { useEffect } from 'react';
import { listen } from '@tauri-apps/api/event';

interface DeepLinkPayload {
  url: string;
}

function DeepLinkHandler() {
  useEffect(() => {
    const unlisten = listen<DeepLinkPayload>('deep-link', (event) => {
      const url = event.payload.url;
      console.log('Deep link received:', url);

      // Parse the deep link URL
      // Format: tracertm://action/params
      const urlObj = new URL(url);
      const action = urlObj.host;
      const params = new URLSearchParams(urlObj.search);

      switch (action) {
        case 'open-requirement':
          const requirementId = params.get('id');
          if (requirementId) {
            console.log('Opening requirement:', requirementId);
            // Navigate to requirement
            window.location.hash = `/requirements/${requirementId}`;
          }
          break;

        case 'open-test':
          const testId = params.get('id');
          if (testId) {
            console.log('Opening test:', testId);
            // Navigate to test
            window.location.hash = `/tests/${testId}`;
          }
          break;

        case 'open-project':
          const projectId = params.get('id');
          if (projectId) {
            console.log('Opening project:', projectId);
            // Navigate to project
            window.location.hash = `/projects/${projectId}`;
          }
          break;

        case 'sync':
          console.log('Triggering sync from deep link');
          // Trigger sync
          break;

        default:
          console.warn('Unknown deep link action:', action);
      }
    });

    return () => {
      unlisten.then((fn) => fn());
    };
  }, []);

  return null; // This component doesn't render anything
}

export default DeepLinkHandler;
