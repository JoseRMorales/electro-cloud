'use client'

import { IconCircleFilled, IconMoonFilled as Moon, IconSunFilled as Sun } from '@tabler/icons-react'
import { Button } from 'flowbite-react'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

const ModeToggle = () => {
  const { theme, setTheme } = useTheme()
  const [icon, setIcon] = useState<JSX.Element>(<IconCircleFilled />)

  // To avoid hydrating errors we should use the Icon element as use state so a default value is sent to the client (Moon) and then when the theme is set by the user or the provider the icon is updated via hydration
  useEffect(() => {
    if (theme === 'dark') {
      setIcon(<Sun />)
    } else {
      setIcon(<Moon />)
    }
  }, [theme])

  return (
    <>
      {theme === 'dark'
        ? (
          <Button onClick={() => { setTheme('light') }} size="xs">
            {icon}
          </Button>
          )
        : (
          <Button onClick={() => { setTheme('dark') }} size="xs">
            {icon}
          </Button>
          )}
    </>
  )
}

export default ModeToggle
