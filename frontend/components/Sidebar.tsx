"use client";
import Link from 'next/link';
import { useTheme } from 'next-themes';
import { Button } from '../components/ui/button';
import { Moon, Sun } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Sidebar() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-card shadow-lg flex flex-col md:w-full md:bottom-0 md:h-16 md:flex-row md:items-center md:justify-between z-40">
      <div className="flex items-center gap-2 p-4 md:p-2">
        <span className="font-bold text-xl">DOCOCR</span>
      </div>
      <nav className="flex-1 flex flex-col gap-2 p-4 md:flex-row md:gap-6 md:p-2 md:items-center">
        <Link href="/" className="hover:text-primary transition-colors">Upload Document</Link>
        <Link href="/history" className="hover:text-primary transition-colors">History</Link>
      </nav>
      <div className="p-4 md:p-2 flex items-center">
        {mounted && (
          <Button variant="ghost" size="icon" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label="Toggle theme">
            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </Button>
        )}
      </div>
    </aside>
  );
}
