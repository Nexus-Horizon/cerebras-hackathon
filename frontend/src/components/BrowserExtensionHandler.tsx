'use client';

import { useEffect } from 'react';

export default function BrowserExtensionHandler({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Remove or handle browser extension attributes that cause hydration mismatches
    const body = document.body;
    if (body) {
      // Remove cz-shortcut-listen attribute if added by ColorZilla extension
      if (body.hasAttribute('cz-shortcut-listen')) {
        body.removeAttribute('cz-shortcut-listen');
      }
    }
  }, []);

  return <>{children}</>;
}
