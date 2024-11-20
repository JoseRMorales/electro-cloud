'use client'

import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'
import { IconClipboard } from '@tabler/icons-react'
import { useEffect, useState } from 'react'

interface DataTableProps {
  data: string
}

const DataTable = ({ data }: DataTableProps) => {
  const { toast } = useToast()
  const [commaSeparator, setCommaSeparator] = useState(false)
  const [formattedData, setFormattedData] = useState(data)

  const header = data.split('\n')[0]

  const firstColumnClass =
    'whitespace-nowrap font-medium text-gray-900 dark:text-white not-selectable'

  const cleanData = (data: string) => {
    // Remove first column and firts row and substitute ; with \t
    const content = data
      .split('\n')
      .slice(1)
      .map((row) => row.split(';').slice(1).join('\t'))
      .join('\n')

    return content
  }

  const launchToast = () => {
    toast({
      description: 'Copied to clipboard'
    })
    console.log('Copied to clipboard')
  }

  const handleCopyToClipboard = () => {
    const content = cleanData(formattedData)
    navigator.clipboard.writeText(content)
    launchToast()
  }

  const handleCopyFirstGroup = () => {
    const content = cleanData(formattedData)
    // Get first group. The first 3 rows
    const firstGroup = content.split('\n').slice(0, 3).join('\n')
    navigator.clipboard.writeText(firstGroup)
    launchToast()
  }

  const handleCopySecondGroup = () => {
    const content = cleanData(formattedData)
    // Get second group. The following 2 rows
    const secondGroup = content.split('\n').slice(3, 5).join('\n')
    navigator.clipboard.writeText(secondGroup)
    launchToast()
  }

  const handleCopyThirdGroup = () => {
    const content = cleanData(formattedData)
    // Get third group. The following 2 rows
    const thirdGroup = content.split('\n').slice(5, 7).join('\n')
    navigator.clipboard.writeText(thirdGroup)
    launchToast()
  }

  const handleCopyFourthGroup = () => {
    const content = cleanData(formattedData)
    // Get fourth group. The following 2 rows
    const fourthGroup = content.split('\n').slice(7, 9).join('\n')
    navigator.clipboard.writeText(fourthGroup)
    launchToast()
  }

  useEffect(() => {
    // Replace . with , and viceversa
    if (commaSeparator) {
      const newData = data
        .split('\n')
        .map((row) => row.replace(/\./g, ','))
        .join('\n')
      setFormattedData(newData)
    } else {
      const newData = data
        .split('\n')
        .map((row) => row.replace(/,/g, '.'))
        .join('\n')
      setFormattedData(newData)
    }
  }, [commaSeparator, data])

  return (
    <>
      <article className="overflow-x-auto w-full">
        <Table>
          <TableHeader>
            <TableRow>
              {header.split(';').map((item, index) => {
                return (
                  <TableHead key={index} className="select-none">
                    {item}
                  </TableHead>
                )
              })}
            </TableRow>
          </TableHeader>
          <TableBody className="divide-y">
            {formattedData
              .split('\n')
              .slice(1)
              .filter((row) => row !== '')
              .map((row, index) => {
                return (
                  <TableRow key={index} className="">
                    {row.split(';').map((item, index) => {
                      return (
                        <TableCell
                          key={index}
                          {...(index === 0 && { className: firstColumnClass })}
                        >
                          {item}
                        </TableCell>
                      )
                    })}
                  </TableRow>
                )
              })}
          </TableBody>
        </Table>
      </article>
      <aside className="flex flex-col gap-16 p-4">
        <div className="flex justify-center gap-16">
          <Button onClick={handleCopyToClipboard}>
            Copy to clipboard
            <IconClipboard className="ml-2" />
          </Button>
          <Button
            onClick={() => {
              setCommaSeparator(!commaSeparator)
            }}
          >
            {commaSeparator
              ? 'Use dot as decimal separator'
              : 'Use comma as decimal separator'}
          </Button>
        </div>
        <div className="flex justify-between gap-16">
          <Button onClick={handleCopyFirstGroup}>
            Copy first group
            <IconClipboard className="ml-2" />
          </Button>
          <Button onClick={handleCopySecondGroup}>
            Copy second group
            <IconClipboard className="ml-2" />
          </Button>
          <Button onClick={handleCopyThirdGroup}>
            Copy third group
            <IconClipboard className="ml-2" />
          </Button>
          <Button onClick={handleCopyFourthGroup}>
            Copy fourth group
            <IconClipboard className="ml-2" />
          </Button>
        </div>
      </aside>
    </>
  )
}
export default DataTable
