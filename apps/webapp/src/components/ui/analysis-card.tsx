'use client'

import { Card } from 'flowbite-react'
import Link from 'next/link'

interface AnalysisCardProps {
  analysisId: string
  holder?: string
  name?: string
}

const AnalysisCard = ({ analysisId, holder, name }: AnalysisCardProps) => {
  return (
    <Link href={`/energy/${analysisId}`}>

      <Card className='max-w-sm'>
        <h5 className='text-2xl font-bold tracking-tight text-gray-900 dark:text-white'>
          <p>
            {analysisId}
          </p>
        </h5>
        {
        holder != null && (
          <p className="font-normal text-gray-700 dark:text-gray-400">
            {holder}
          </p>
        )
      }
        {
          name != null && (
            <p className="font-normal text-gray-700 dark:text-gray-400">
              {name}
            </p>
          )
        }
      </Card>
    </Link>
  )
}
export default AnalysisCard
