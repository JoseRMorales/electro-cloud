'use client'

import { Table } from 'flowbite-react'

interface DataTableProps {
  data: string
}

const DataTable = ({ data }: DataTableProps) => {
  const header = data.split('\n')[0]

  const firstColumnClass = 'whitespace-nowrap font-medium text-gray-900 dark:text-white'

  return (
    <article className='overflow-x-auto md:w-full'>
      <Table>
        <Table.Head>
          {
        header.split(';').map((item, index) => {
          return (
            <Table.HeadCell key={index}>
              {item}
            </Table.HeadCell>
          )
        })
      }
        </Table.Head>
        <Table.Body className='divide-y'>
          {
        data.split('\n').slice(1).filter((row) => row !== '').map((row, index) => {
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
  )
}
export default DataTable
