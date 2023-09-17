'use client'
import { Navbar } from 'flowbite-react'
import Link from 'next/link'
import { ModeToggle } from './ui/mode-toggle'

const navigations: {name: string, href: string}[] = [
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

const Header = () => {
  return (
    <Navbar
      fluid
      rounded
    >
      <Navbar.Brand as={Link} href="/">
        <span className="self-center whitespace-nowrap text-xl font-semibold dark:text-white">
          Electro Cloud
        </span>
      </Navbar.Brand>
      <Navbar.Collapse>
        {
          navigations.map((navigation) => (
            <Navbar.Link as={Link} href={navigation.href} key={navigation.name}>
              {navigation.name}
            </Navbar.Link>
          ))
        }
      </Navbar.Collapse>
      <div>
        <ModeToggle />
        <Navbar.Toggle />
      </div>
    </Navbar>

  )
}

export default Header
