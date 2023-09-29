'use client'

import { Navbar } from 'flowbite-react'
import Link from 'next/link'

import ModeToggle from './ui/mode-toggle'

const routes: Array<{ name: string, href: string }> = [
  {
    name: 'Home',
    href: '/'
  },
  {
    name: 'Energy',
    href: '/energy'
  },
  {
    name: 'Solar',
    href: '/solar'
  }
]

const LayoutNavbar = () => {
  return (
    <Navbar
        fluid
        rounded
        className='bg-slate-200 dark:bg-slate-900'
    >
      <div className="flex md:order-2 gap-4">
        <ModeToggle />
        <Navbar.Toggle />
      </div>
      <Navbar.Brand as={Link} href="/">
        <h1>Electro Cloud</h1>
      </Navbar.Brand>
      <Navbar.Collapse>
        {
          routes.map((route) => (
            <Navbar.Link
              as={Link}
              href={route.href}
              key={route.name}>
              {route.name}
            </Navbar.Link>
          ))
        }
      </Navbar.Collapse>
    </Navbar>
  )
}

export default LayoutNavbar
