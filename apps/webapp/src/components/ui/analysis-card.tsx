'use client'

import { Button, Card } from 'flowbite-react'
import Link from 'next/link'
import { useState } from 'react'

import { deleteAnalysis } from '@/actions/energy-form'

interface AnalysisCardProps {
  analysisId: string
  created_at: string
}

const AnalysisCard = ({ analysisId, created_at }: AnalysisCardProps) => {
  const [pending, setPending] = useState(false)

  const handleClick = () => {
    setPending(true)
  }

  const date = new Date(created_at).toLocaleString('es-ES', {
    timeZone: 'Europe/Madrid'
  })

  const deleteAnalysisWithId = deleteAnalysis.bind(null, analysisId)
  return (
    <Card className="max-w-sm hover:scale-105 transform transition-all duration-200">
      <Link
        href={`/energy/${analysisId}`}
        className="inline-block relative z-10 p-8 -m-8"
      >
        <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          <p>{analysisId}</p>
        </h5>
        <p>Created at: {date}</p>
      </Link>
      <form action={deleteAnalysisWithId}>
        <Button
          type="submit"
          size="xs"
          color="failure"
          className="w-full mt-6"
          onClick={handleClick}
          isProcessing={pending}
        >
          Delete
        </Button>
      </form>
    </Card>
  )
}
export default AnalysisCard
