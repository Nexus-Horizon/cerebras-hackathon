'use client';

import Image from 'next/image';
import { useRouter } from 'next/navigation';

const Logo = () => {
  const router = useRouter();

  const handleClick = () => {
    router.push('/');
  };

  return (
    <button
      onClick={handleClick}
      className="fixed top-4 left-4 z-50 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors duration-200"
      aria-label="Go to home page"
    >
      <Image
        src="/android-chrome-192x192.png"
        alt="Logo"
        width={32}
        height={32}
        className="w-8 h-8"
      />
    </button>
  );
};

export default Logo; 