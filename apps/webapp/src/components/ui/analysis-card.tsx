'use client'

import { deleteAnalysis } from '@/actions/energy-form'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
// @ts-ignore
import { type apiType } from '@/types/types'
import { useFormStatus } from 'react-dom'

interface AnalysisCardProps {
  analysisId: string
  created_at: string
  api: apiType
}

const AnalysisCard = ({ analysisId, created_at, api }: AnalysisCardProps) => {
  const { pending } = useFormStatus()

  const date = new Date(created_at).toLocaleString('es-ES', {
    timeZone: 'Europe/Madrid',
  })

  const deleteAnalysisWithId = deleteAnalysis.bind(null, analysisId)
  return (
    <div className="max-w-sm hover:scale-105 transform transition-all duration-200 rounded-md p-4 bg-white dark:bg-gray-800 shadow-lg">
      <Link
        href={`/${api}/${analysisId}`}
        className="inline-block relative z-10 p-8 -m-8"
      >
        <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          <p>{analysisId}</p>
        </h5>
        <p>Created at: {date}</p>
      </Link>
      <form action={deleteAnalysisWithId}>
        <Button
          variant="destructive"
          type="submit"
          className="w-full mt-6 hover:bg-red-600"
          disabled={pending}
        >
          Delete
        </Button>
      </form>
    </div>
  )
}
export default AnalysisCard
