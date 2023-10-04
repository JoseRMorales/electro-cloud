'use client'

import { IconClipboard } from '@tabler/icons-react'
import { Button, Table, Toast } from 'flowbite-react'
import { useEffect, useState } from 'react'

interface DataTableProps {
  data: string
}

const DataTable = ({ data }: DataTableProps) => {
  const [toast, setToast] = useState(false)
  const [commaSeparator, setCommaSeparator] = useState(false)
  const [formattedData, setFormattedData] = useState(data)

  const header = data.split('\n')[0]

  const firstColumnClass = 'whitespace-nowrap font-medium text-gray-900 dark:text-white not-selectable'

  const cleanData = (data: string) => {
    // Remove first column and firts row and substitute ; with \t
    const content = data.split('\n').slice(1).map((row) => row.split(';').slice(1).join('\t')).join('\n')
    return content
  }

  const launchToast = () => {
    setToast(true)
    // Hide toast after 3 seconds
    setTimeout(() => {
      setToast(false)
    }, 3000)
  }

  const handleCopyToClipboard = () => {
    const content = cleanData(data)
    navigator.clipboard.writeText(content)
    launchToast()
  }

  const handleCopyFirstGroup = () => {
    const content = cleanData(data)
    // Get first group. The first 3 rows
    const firstGroup = content.split('\n').slice(0, 3).join('\n')
    navigator.clipboard.writeText(firstGroup)
    launchToast()
  }

  const handleCopySecondGroup = () => {
    const content = cleanData(data)
    // Get second group. The following 2 rows
    const secondGroup = content.split('\n').slice(3, 5).join('\n')
    navigator.clipboard.writeText(secondGroup)
    launchToast()
  }

  const handleCopyThirdGroup = () => {
    const content = cleanData(data)
    // Get third group. The following 2 rows
    const thirdGroup = content.split('\n').slice(5, 7).join('\n')
    navigator.clipboard.writeText(thirdGroup)
    launchToast()
  }

  const handleCopyFourthGroup = () => {
    const content = cleanData(data)
    // Get fourth group. The following 2 rows
    const fourthGroup = content.split('\n').slice(7, 9).join('\n')
    navigator.clipboard.writeText(fourthGroup)
    launchToast()
  }

  useEffect(() => {
    // Replace . with , and viceversa
    if (commaSeparator) {
      const newData =
        data
          .split('\n')
          .map((row) => row.replace(/\./g, ','))
          .join('\n')
      setFormattedData(newData)
    } else {
      const newData =
        data
          .split('\n')
          .map((row) => row.replace(/,/g, '.'))
          .join('\n')
      setFormattedData(newData)
    }
  }, [commaSeparator])

  return (
    <>
      <article className='overflow-x-auto w-full'>
        <Table>
          <Table.Head>
            {
        header.split(';').map((item, index) => {
          return (
            <Table.HeadCell key={index} className='select-none'>
              {item}
            </Table.HeadCell>
          )
        })
      }
          </Table.Head>
          <Table.Body className='divide-y'>
            {
        formattedData.split('\n').slice(1).filter((row) => row !== '').map((row, index) => {
          return (
            <Table.Row key={index} className='bg-white dark:border-gray-700 dark:bg-gray-800'>
              {
              row.split(';').map((item, index) => {
                return (
                  <Table.Cell key={index} { ...(index === 0 && { className: firstColumnClass }) }>
                    {item}
                  </Table.Cell>
                )
              })
            }
            </Table.Row>
          )
        })
      }
          </Table.Body>
        </Table>
      </article>
      <aside className='flex flex-col gap-16 p-4'>
        <div className='flex justify-center gap-16'>
          <Button onClick={handleCopyToClipboard}>
            Copy to clipboard
            <IconClipboard className='ml-2' />
          </Button>
          <Button onClick={() => { setCommaSeparator(!commaSeparator) }}>
            {commaSeparator ? 'Use dot as decimal separator' : 'Use comma as decimal separator'}
          </Button>
        </div>
        <div className='flex justify-between gap-16'>
          <Button onClick={handleCopyFirstGroup}>
            Copy first group
            <IconClipboard className='ml-2' />
          </Button>
          <Button onClick={handleCopySecondGroup}>
            Copy second group
            <IconClipboard className='ml-2' />
          </Button>
          <Button onClick={handleCopyThirdGroup}>
            Copy third group
            <IconClipboard className='ml-2' />
          </Button>
          <Button onClick={handleCopyFourthGroup}>
            Copy fourth group
            <IconClipboard className='ml-2' />
          </Button>
        </div>
      </aside>
      {
        toast &&
        (<Toast>
          <div className="ml-3 text-sm font-normal">
            <p className="text-gray-600 dark:text-gray-300">Copied to clipboard</p>
          </div>
        </Toast>)
      }
    </>
  )
}
export default DataTable
